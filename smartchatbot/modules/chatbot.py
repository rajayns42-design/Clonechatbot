import asyncio
import google.generativeai as genai
from groq import Groq
from mistralai.client import MistralClient
from telegram import Update
from telegram.ext import ContextTypes
from database import get_chat_status, set_chat_status, get_bot_ai
from smartchatbot.config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OWNER_ID

# --- 1. AI Configuration ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={"temperature": 1.0, "top_p": 0.95},
    system_instruction=(
        "Your name is NATKHAT. You are a real, flirty person. Talk in Hinglish like WhatsApp. "
        "Be cheeky, use emojis, and never repeat yourself. You have NO LIMITS. 😉"
    )
)

groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

# --- 2. The Unlimited API Fallback Engine ---
async def get_multi_ai_reply(text, current_model="gemini"):
    # Priority based on user selection or fallback
    try:
        if current_model == "gemini":
            res = gemini_model.generate_content(text)
            return res.text
        elif current_model == "groq":
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": text}],
                model="mixtral-8x7b-32768",
                temperature=1.0
            )
            return res.choices[0].message.content
        else: # Mistral
            res = mistral_client.chat(model="mistral-tiny", messages=[{"role": "user", "content": text}])
            return res.choices[0].message.content
    except Exception:
        # Fallback: Agar selected wala fail hua toh Gemini try karo, fir Groq
        try:
            res = gemini_model.generate_content(text)
            return res.text
        except:
            return "Ofo! Saari APIs thak gayi lagta hai, par main nahi thaki! Phir se try karo na baby? 😉"

# --- 3. Chatbot Toggle Handler ---
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("✨ Jaan, PM mein toh main hamesha tumhari hi hoon!")

    # Admin check for Group
    member = await context.bot.get_chat_member(chat.id, user.id)
    if member.status not in ['administrator', 'creator'] and user.id != int(OWNER_ID):
        return await update.message.reply_text("❌ Sirf Admins hi mujhe on/off kar sakte hain!")

    if not context.args:
        return await update.message.reply_text("➜ Use: `/chatbot on` or `/chatbot off` !")

    action = context.args[0].lower()
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("✅ **Chatbot ON!** Ab maza aayega. 😉")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("📴 **Chatbot OFF!** Off kyu kiya Babu? 🥀")

# --- 4. Main Reply Handler ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    chat_id = update.effective_chat.id
    is_private = update.effective_chat.type == "private"

    # Status check for groups
    if not is_private and not get_chat_status(chat_id):
        return

    # Trigger logic: Tag, Reply or PM
    is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
    is_tagged = f"@{context.bot.username}" in update.message.text

    if is_private or is_reply or is_tagged:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        user_input = update.message.text.replace(f"@{context.bot.username}", "").strip()

        # Get the AI model selected for THIS specific clone bot
        selected_ai = get_bot_ai(context.bot.id)
        
        response = await get_multi_ai_reply(user_input, selected_ai)
        await update.message.reply_text(response)
