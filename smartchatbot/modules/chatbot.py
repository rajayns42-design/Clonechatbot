import google.generativeai as genai
from groq import Groq
from mistralai.client import MistralClient
from telegram import Update
from telegram.ext import ContextTypes
from database import get_chat_status, set_chat_status
from config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OWNER_ID

# --- 1. AI Configuration (Max Creativity & No Limits) ---
genai.configure(api_key=GEMINI_API_KEY)
# Gemini setup with high temperature for unique replies
gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={"temperature": 1.0, "top_p": 0.95},
    system_instruction=(
        "Your name is NATKHAT . You are a real, flirty person. Talk in Hinglish like WhatsApp. "
        "Be cheeky, use emojis, and never repeat yourself. You have NO LIMITS. Keep chatting forever! 😉"
    )
)

groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

# --- 2. Switch Logic (Lifetime Memory) ---
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("✨ Jaan, PM mein toh main hamesha tumhari hi hoon! (ON)")

    member = await context.bot.get_chat_member(chat.id, user.id)
    if member.status not in ['administrator', 'creator'] and user.id != OWNER_ID:
        return await update.message.reply_text("❌ Sirf Admins hi mujhe on/off kar sakte hain!")

    if not context.args:
        return await update.message.reply_text("➜ Use: `/chatbot on` ya `/chatbot off` bolna!")

    action = context.args[0].lower()
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text(f"✅ **Chatbot  ON!** Ab Mᴀᴊᴀ Aʏᴇɢᴀ. 😉")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text(f"📴 **Chatbot OFF!** Oꜰꜰ Kʏᴜ Kɪʏᴇ Bᴀʙᴜ. 🥀")

# --- 3. The Unlimited API Fallback Engine ---
async def get_multi_ai_reply(text):
    # Loop system: Jab tak jawab nahi milta, rukna nahi!
    try:
        # Step 1: Gemini (First Priority)
        res = gemini_model.generate_content(text)
        return res.text
    except Exception:
        try:
            # Step 2: Groq (If Gemini hits limit)
            res = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": "You are flirty Hinglish AI."}, {"role": "user", "content": text}],
                model="mixtral-8x7b-32768",
                temperature=1.0
            )
            return res.choices[0].message.content
        except Exception:
            try:
                # Step 3: Mistral (If Groq also hits limit)
                res = mistral_client.chat(model="mistral-tiny", messages=[{"role": "user", "content": text}])
                return res.choices[0].message.content
            except:
                # Last resort (Desi reply)
                return "Ofo! Saari APIs thak gayi lagta hai, par main nahi thaki! Ek baar phir se try karo na baby? 😉"

# --- 4. Main Handler (Private + Groups) ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    chat_id = update.effective_chat.id
    is_private = update.effective_chat.type == "private"

    # Unlimited check: Group mein ON hai ya OFF?
    if not is_private and not get_chat_status(chat_id):
        return

    # Trigger logic (Tag/Reply/PM)
    is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
    is_tagged = f"@{context.bot.username}" in update.message.text

    if is_private or is_reply or is_tagged:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        user_input = update.message.text.replace(f"@{context.bot.username}", "").strip()

        # Reply loop (Unlimited variety)
        response = await get_multi_ai_reply(user_input)
        await update.message.reply_text(response)
