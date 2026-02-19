import asyncio
import random
import re
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral
from telegram import Update
from telegram.ext import ContextTypes

# --- CONFIG & DATABASE IMPORTS ---
from ..database import get_chat_status, set_chat_status
from ..config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OWNER_ID

# --- 1. AI Configuration (Tuned for Ultra-Short Replies) ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={
        "temperature": 0.8, 
        "top_p": 1,
        "max_output_tokens": 25, # Isse zyada AI bol hi nahi payega
    },
    system_instruction=(
        "Tera naam NATKHAT hai. Tu ek chulbuli ladki hai. "
        "STRICT RULE: Reply should be ONLY 3 to 5 words. " #
        "Use Hinglish and only 1 emoji. Do NOT use double quotes in your response."
    )
)

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def clean_for_telegram(text):
    """Heroku offset error fix karne ke liye text cleaning"""
    # Double quotes aur unnecessary formatting hatao
    text = text.replace('"', '').replace('`', '').strip()
    # HTML special characters escape
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text

# --- 2. Short Reply Engine ---
async def get_multi_ai_reply(text):
    prompt = f"Short Hinglish reply to: {text} (Max 5 words)"
    response_text = ""

    if GEMINI_API_KEY:
        try:
            res = gemini_model.generate_content(prompt)
            if res.text: response_text = res.text
        except: pass

    if not response_text and groq_client:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                max_tokens=20
            )
            response_text = res.choices[0].message.content
        except: pass

    if response_text:
        # Sirf pehli line lo aur quotes saaf karo
        final = clean_for_telegram(response_text.split('\n')[0])
        return final[:60] # Aur chota rakho

    return random.choice(["Ofo, nakhre! 😉", "Arey wah! ✨", "Tum bhi na.. 🙈"])

# --- 3. Chatbot Toggle ---
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("Jaan, PM mein toh main on hi hoon! 😉")

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator'] and user.id != OWNER_ID:
            return await update.message.reply_text("❌ Admin power chahiye iske liye!")
    except: return

    action = context.args[0].lower() if context.args else ""
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("✅ <b>chatbot ON!</b> Ab maza aayega. 😉", parse_mode="HTML")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("📴 <b>chatbot OFF!</b> Bye baby. 🥀", parse_mode="HTML")
    else:
        status = "ON ✅" if get_chat_status(chat.id) else "OFF ❌"
        await update.message.reply_text(f"Abhi status {status} hai. Use `/chatbot on/off`")

# --- 4. Main Handler ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    chat_id = update.effective_chat.id
    if update.effective_chat.type != "private" and not get_chat_status(chat_id):
        return

    is_reply = (update.message.reply_to_message and 
                update.message.reply_to_message.from_user.id == context.bot.id)
    
    if update.effective_chat.type == "private" or is_reply or f"@{context.bot.username}" in update.message.text:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        user_input = update.message.text.replace(f"@{context.bot.username}", "").strip()
        
        reply = await get_multi_ai_reply(user_input)
        
        try:
            # HTML mode use karna sabse safe hai
            await update.message.reply_text(reply, parse_mode="HTML")
        except:
            await update.message.reply_text(reply) # Raw text backup
