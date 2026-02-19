import asyncio
import random
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral
from telegram import Update
from telegram.ext import ContextTypes

# --- FIXED RELATIVE IMPORTS ---
from ..database import get_chat_status, set_chat_status
from ..config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OWNER_ID

# --- 1. AI Configuration ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={
        "temperature": 0.9, # Varied randomness
        "top_p": 1,
        "max_output_tokens": 100,
    },
    system_instruction=(
        "Tera naam NATKHAT hai. Tu ek bahut hi pyaari, chulbuli aur natkhat ladki hai. "
        "WhatsApp par jaise doston se baat karte hain waise Hinglish mein baat kar. "
        "Ek hi jawab baar baar mat dena (DO NOT REPEAT). Har baar kuch naya aur cheeky bol. "
        "Emojis use kar (😉, ✨, 🙈, 🔥). Replies ekdum short aur sweet rakh."
    )
)

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

# --- 2. The Unlimited Switching Engine (No-Repeat Logic) ---
async def get_multi_ai_reply(text):
    # Prompt mein randomness add ki gayi hai taaki AI naya soche
    prompt = f"User ne kaha: {text}. Iska ek naya aur unique Hinglish reply do (sirf 1 line, flirty style)."
    
    # 1. Gemini (Primary)
    if GEMINI_API_KEY:
        try:
            res = gemini_model.generate_content(prompt)
            if res.text: return res.text
        except Exception: pass

    # 2. Groq (Backup)
    if groq_client:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=1.0 # High temperature for unique replies
            )
            return res.choices[0].message.content
        except Exception: pass

    # 3. Mistral (Backup 2)
    if mistral_client:
        try:
            res = mistral_client.chat.complete(
                model="mistral-small-latest", 
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content
        except Exception: pass

    # Cute Final Fallbacks (Agar sab fail ho jayein)
    fallbacks = [
        "Arey yaar, itni baatein karoge toh thak jaungi na! 😉✨",
        "Abhi mood nahi hai batane ka, thodi der mein puchna baby! 🙈",
        "Tumhari baaton mein kho gayi thi, kya pucha fir se bolo? 😘",
        "Ofo! Network nakhre dikha raha hai meri tarah. 🥀"
    ]
    return random.choice(fallbacks)

# --- 3. Chatbot Toggle Handler ---
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("Jaan, PM mein toh main hamesha on hi hoon! 😉✨")

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator'] and user.id != OWNER_ID:
            return await update.message.reply_text("❌ Sirf Admins mujhe control kar sakte hain!")
    except: return

    if not context.args:
        status = "ON ✅" if get_chat_status(chat.id) else "OFF ❌"
        return await update.message.reply_text(f"Abhi status {status} hai. Badalne ke liye `/chatbot on/off` use karein.")

    action = context.args[0].lower()
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("✅ **NATKHAT ON!** Ab shuru karte hain masti. 😉")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("📴 **NATKHAT OFF!** Bye bye, miss karna mujhe. 🥀")

# --- 4. Main Reply Handler ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    chat_id = update.effective_chat.id
    is_private = update.effective_chat.type == "private"

    if not is_private and not get_chat_status(chat_id):
        return

    is_reply = (update.message.reply_to_message and 
                update.message.reply_to_message.from_user.id == context.bot.id)
    is_tagged = f"@{context.bot.username}" in update.message.text

    if is_private or is_reply or is_tagged:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        user_input = update.message.text.replace(f"@{context.bot.username}", "").strip()
        
        response = await get_multi_ai_reply(user_input)
        await update.message.reply_text(response)
