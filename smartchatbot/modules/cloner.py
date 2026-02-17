import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Modules & DB Imports
from modules.chatbot import chatbot_reply, chatbot_toggle 
from modules.welcome import welcome_toggle, welcome_member 
from modules.admin import ban_user, mute_user, promote_user, get_admin_list 
from database import add_cloned_bot, remove_cloned_bot, chats_collection # DB se chats lene ke liye
from config import API_ID, API_HASH, OWNER_ID # Real Owner ID zaroori hai

# Memory cache for active clones
CLONES = {}

# --- 1. Master-Only Broadcast Logic ---
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Strict Check: Sirf Main Owner ID hi chalegi
    if user_id != int(OWNER_ID):
        return await update.message.reply_text("❌ **Dafa ho jao!** Ye command sirf mere asli malik ke liye hai. 😉")

    if not update.message.reply_to_message:
        return await update.message.reply_text("➜ **Jaan, reply toh karo!** Kisi message par reply karke `/broadcast` likho.")

    msg = update.message.reply_to_message
    status_msg = await update.message.reply_text("📢 **Broadcasting...** Sabhi groups mein message ja raha hai.")
    
    all_chats = chats_collection.find()
    success, failed = 0, 0

    for chat in all_chats:
        try:
            await context.bot.copy_message(
                chat_id=chat['chat_id'],
                from_chat_id=msg.chat_id,
                message_id=msg.message_id
            )
            success += 1
            await asyncio.sleep(0.3) # Flood wait se bachne ke liye
        except Exception:
            failed += 1

    await status_msg.edit_text(f"✅ **Broadcast Done!**\n\n🚀 Success: {success}\n❌ Failed: {failed}")

# --- Register All Handlers ---
def register_all_handlers(app: Application):
    # Commands
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    
    # Broadcast (Registering it here but only OWNER_ID can use it)
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    
    # Admin Tools
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("promote", promote_user))

    # Message & Status Logic
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

# --- 2. CLONE Command (With Guide) ---
async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        guide = (
            "✨ **Clone Kaise Karein?**\n\n"
            "1️⃣ @BotFather se token lein.\n"
            "2️⃣ Likhein: `/clone <token>`\n\n"
            "⚠️ **Note:** Broadcast sirf Real Owner kar sakta hai."
        )
        return await update.message.reply_text(guide)

    bot_token = context.args[0]
    try:
        app = Application.builder().token(bot_token).build()
        register_all_handlers(app)
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        bot_info = await app.bot.get_me()
        add_cloned_bot(user_id, bot_token, bot_info.username, bot_info.id)
        CLONES[bot_token] = app
        await update.message.reply_text(f"✅ **Clone Active!** @{bot_info.username}")
    except Exception:
        await update.message.reply_text("❌ Error! Token check karein.")

# --- 3. DE-CLONE Command ---
async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("➜ Token do!")
    token = context.args[0]
    if token in CLONES:
        await CLONES[token].updater.stop()
        await CLONES[token].stop()
        del CLONES[token]
    remove_cloned_bot(token)
    await update.message.reply_text("🗑️ Clone deleted successfully!")

# --- 4. Start Message ---
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name
    welcome_text = (
        f"𝖧𝖾𝗒 **{user.first_name}** ✨\n𝖨'𝗆 **{bot_name}**\n\n"
        "➜ 𝖨’𝗆 𝖠 𝖲𝗆𝖺𝗋𝗍 𝖠𝖨 𝖢𝗁𝖺𝗍 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍\n"
        "➜ 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖥𝗋𝖾𝖾 `/clone` 𝖥𝖾𝖺𝗍𝗎𝗋𝖾\n"
    )
    buttons = [[InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')
