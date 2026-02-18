import os
import asyncio
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- FIXED RELATIVE IMPORTS (Heroku Fix) ---
from .welcome import welcome_toggle, welcome_member 
from .admin import ban_user, mute_user, promote_user
from ..database import add_cloned_bot, remove_cloned_bot, chats_collection
from ..config import (
    API_ID, API_HASH, OWNER_ID, CLONE_LOGGER, 
    GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY
)

# --- AI SETUP ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

CLONES = {}

# --- AI Multi-Engine Logic ---
async def get_ai_reply(text):
    if GEMINI_API_KEY:
        try:
            response = gemini_model.generate_content(text)
            if response and response.text:
                return response.text
        except Exception: pass 

    if groq_client:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": text}],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except Exception: pass

    if mistral_client:
        try:
            chat_response = mistral_client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": text}],
            )
            return chat_response.choices[0].message.content
        except Exception: pass

    return "❌ Sorry meri jaan, saare AI engines busy hain!"

# --- Chatbot Handler ---
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await get_ai_reply(update.message.text)
    await update.message.reply_text(reply)

# --- Register Handlers (Master + Clone) ---
def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

# --- CLONE Command ---
async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("✨ `/clone <token>` likho!")

    token = context.args[0]
    m = await update.message.reply_text("🚀 **Setup ho raha hai...**")
    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app)
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        bot_info = await app.bot.get_me()
        add_cloned_bot(update.effective_user.id, token, bot_info.username, bot_info.id)
        CLONES[token] = app
        
        await m.edit_text(f"✅ **Clone Active!**\n🤖 Bot: @{bot_info.username}")
    except Exception as e:
        await m.edit_text(f"❌ Error: {str(e)}")

# --- DE-CLONE Command ---
async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    token = context.args[0]
    if token in CLONES:
        await CLONES[token].stop()
        del CLONES[token]
    remove_cloned_bot(token)
    await update.message.reply_text("🗑️ Clone deleted successfully!")

# --- Original Start Handler ---
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"𝖧𝖾𝗒 **{user.first_name}** ✨\n\n"
        "➜ 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 `/clone` 𝖥𝖾𝖺𝗍𝗎𝗋𝖾\n"
        "➜ Fast AI Responseà\n"
        "➜ Hᴜᴍᴀɴ ʟɪᴋᴇ ʀᴇᴩʟʏ\n"
        "➜ 24×7 Oɴʟɪɴᴇ Fᴀꜱᴛ ʀᴇᴩʟʏ\n"
    )
    btns = [[InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode='Markdown')

# --- Master Broadcast ---
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != int(OWNER_ID):
        return await update.message.reply_text("❌ Sirf Malik ke liye!")
    
    if not update.message.reply_to_message:
        return await update.message.reply_text("Kisi message par reply karke `/broadcast` likho!")

    msg = update.message.reply_to_message
    all_chats = chats_collection.find()
    success, failed = 0, 0

    for chat in all_chats:
        try:
            await context.bot.copy_message(chat_id=chat['chat_id'], from_chat_id=msg.chat_id, message_id=msg.message_id)
            success += 1
            await asyncio.sleep(0.3)
        except: failed += 1
    
    await update.message.reply_text(f"✅ Broadcast Done!\n🚀 Success: {success}\n❌ Failed: {failed}")
