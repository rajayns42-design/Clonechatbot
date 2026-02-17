import os
import asyncio
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Modules & DB Imports
from modules.welcome import welcome_toggle, welcome_member 
from modules.admin import ban_user, mute_user, promote_user
from database import add_cloned_bot, remove_cloned_bot, chats_collection
from config import (
    API_ID, API_HASH, OWNER_ID, CLONE_LOGGER, 
    GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY
)

# --- AI ENGINES SETUP (Using Config Vars) ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Client setup tabhi hoga jab keys available honge
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

# Memory cache for active clones
CLONES = {}

# --- AI Multi-Engine Logic (No Repeat Fallback) ---
async def get_ai_reply(text):
    """Teeno AI engines ko bari-bari check karega"""
    
    # 1. Gemini (Primary)
    if GEMINI_API_KEY:
        try:
            response = gemini_model.generate_content(text)
            if response.text: return response.text
        except Exception: pass

    # 2. Groq (First Backup)
    if groq_client:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": text}],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except Exception: pass

    # 3. Mistral (Final Backup)
    if mistral_client:
        try:
            chat_response = mistral_client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": text}],
            )
            return chat_response.choices[0].message.content
        except Exception: pass

    return "❌ Sorry, abhi koi AI reply nahi de pa raha hai."

# --- Chatbot Handler ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # Typing action for realism
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    reply = await get_ai_reply(update.message.text)
    await update.message.reply_text(reply)

# --- Handlers & Clone Logic ---
def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    # Text messages handle karne ke liye
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

# ... (clone_bot, delclone_bot, aur start_handler ka baki code wahi rahega)
