import asyncio
import random
import re
import google.generativeai as genai
from telegram import Update
from telegram.ext import ContextTypes

# --- CONFIG & DATABASE IMPORTS ---
from ..database import get_chat_status, set_chat_status
from ..config import GEMINI_API_KEY, OWNER_ID

# --- 1. AI Configuration (Tuned for Ultra-Short Replies) ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={
        "temperature": 0.8, 
        "max_output_tokens": 20, # Response size chota rakhne ke liye
    },
    system_instruction=(
        "Tera naam NATKHAT hai. Tu ek chulbuli ladki hai. "
        "STRICT RULE: Reply should be ONLY 3 to 5 words. "
        "Hinglish use kar aur 1 emoji daal. Quotes bilkul mat use kar."
    )
)

def clean_for_telegram(text):
    """'Byte offset' error fix karne ke liye"""
    # Saare quotes aur special symbols hatao jo parsing fail karte hain
    text = text.replace('"', '').replace("'", "").replace('`', '').strip()
    # HTML safe characters
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text

# --- 2. Short Reply Engine ---
async def get_ai_reply(text):
    prompt = f"Short Hinglish reply to: {text} (Max 5 words)"
    try:
        res = gemini_model.generate_content(prompt)
        if res.text:
            # Sirf pehli line aur clean text
            return clean_for_telegram(res.text.split('\n')[0])
    except:
        pass
    return random.choice(["Ofo, nakhre! 😉", "Arey wah! ✨", "Tum bhi na.. 🙈"])

# --- 3. Chatbot Toggle ---
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("Jaan, PM mein toh main hamesha on hi hoon! 😉")

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator'] and user.id != OWNER_ID:
            return await update.message.reply_text("❌ Admin power chahiye baby!")
    except: return

    action = context.args[0].lower() if context.args else ""
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("✅ <b>NATKHAT ON!</b> Masti shuru. 😉", parse_mode="HTML")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("📴 <b>NATKHAT OFF!</b> Bye bye. 🥀", parse_mode="HTML")

# --- 4. Main Reply Handler ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    chat_id = update.effective_chat.id
    # Check if chatbot is on for groups
    if update.effective_chat.type != "private" and not get_chat_status(chat_id):
        return

    is_reply = (update.message.reply_to_message and 
                update.message.reply_to_message.from_user.id == context.bot.id)
    
    # Private chat, reply to bot, or tagging bot
    if update.effective_chat.type == "private" or is_reply or f"@{context.bot.username}" in update.message.text:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        user_input = update.message.text.replace(f"@{context.bot.username}", "").strip()
        
        reply = await get_ai_reply(user_input)
        
        try:
            # HTML mode offset errors ke liye sabse best hai
            await update.message.reply_text(reply, parse_mode="HTML")
        except:
            await update.message.reply_text(reply)
