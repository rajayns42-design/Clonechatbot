import asyncio
import time
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# =========================
# CONFIG & DATABASE IMPORTS
# =========================
from ..config import (
    OWNER_ID, GEMINI_API_KEY, LOGGER_GROUP, CLONE_LOGGER, 
    START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL
)
from ..database import (
    add_cloned_bot, remove_cloned_bot, users_collection, 
    set_welcome_status, get_welcome_status, get_chat_status, set_chat_status
)
from .welcome import welcome_member
from .admin import ban_user, unban_user, mute_user, unmute_user
from .chatbot import chatbot_reply 

# =========================
# 🔄 LOGGER SYSTEM
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    text = (
        "👤 **NEW USER STARTED!**\n\n"
        f"🤖 **Bot Name:** {bot.first_name} (@{bot.username})\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"📝 **Name:** {user.first_name}\n"
        f"🏷 **Username:** @{user.username if user.username else 'N/A'}"
    )
    try:
        await context.bot.send_message(chat_id=LOGGER_GROUP, text=text, parse_mode="Markdown")
    except: pass

# =========================
# 🚀 PING & START HANDLERS (IMAGE STYLE)
# =========================

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    bot = await context.bot.get_me()
    
    # Message sending animation
    msg = await update.message.reply_text("⚡")
    
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 3)
    
    # Image ke jaisa text format
    text = (
        f"нᴇу вαву!!\n"
        f"╰─ **{bot.first_name}** 🍓 Is αℓινє 🥀 αη∂ ωᴏяᴋιηɢ\n"
        f"ғιηє ωιтн α ριηɢ ᴏғ\n"
        f"➡ {ping_ms} ms\n\n"
        f"мα∂є ωιтн ❤️ ву   [𝐇𝐀𝐑𝐈 <3](tg://user?id={OWNER_ID}) 🥀"
    )
    
    buttons = [
        [InlineKeyboardButton("ADD ME BABY", url=f"https://t.me/{bot.username}?startgroup=true")],
        [InlineKeyboardButton("CLOSE", callback_data="close_msg")]
    ]
    
    # Agar START_IMG available hai toh photo ke saath bhejega
    if START_IMG:
        await update.message.reply_photo(
            photo=START_IMG, 
            caption=text, 
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
        await msg.delete()
    else:
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    await log_user_start(update, context)

    # Nelumi Style Buttons
    buttons = [
        [InlineKeyboardButton("𝐀𝐃𝐃 𝐌𝐄 𝐁𝐀𝐁𝐘", url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("𝐇𝐄𝐋𝐏", callback_data="clone_help"), 
            InlineKeyboardButton("𝐇𝐀𝐑𝐈", url=f"tg://user?id={OWNER_ID}") 
        ],
        [
            InlineKeyboardButton("📢 𝐔𝐏𝐃𝐀𝐓𝐄", url=UPDATE_CHANNEL),
            InlineKeyboardButton("💬 𝐒𝐔𝐏𝐏𝐎𝐑𝐓", url=SUPPORT_GROUP)
        ]
    ]
    
    text = (
        f"нᴇу [ {user.first_name} ](tg://user?id={user.id}) ✨\n\n"
        f"I'm **{bot.first_name}** 🤖\n\n"
        "๏ **𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?**\n"
        "➜ 𝖨’𝗆 𝖠 𝖲𝗆𝖺𝗋𝗍 𝖠𝖨 𝖢𝗁𝖺𝗍 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍\n"
        "➜ 𝖧𝗎𝗆𝖺𝗇-𝖫𝗂𝗄𝖾 𝖢𝗈𝗇𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗈𝗇𝗌\n"
        "➜ With Unlimited /Clone Features\n\n"
        "➜ **𝖢𝗅𝗂𝖼𝗄 𝖳𝗁𝖾 𝖧𝖾𝗅𝗉 𝖡𝗎𝗍𝗍𝗈𝗇 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌** 💜"
    )

    if update.message:
        await update.message.reply_photo(photo=START_IMG, caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

# =========================
# 🛠 CLONE & CALLBACKS
# =========================

async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("🚀 Usage: `/clone TOKEN`")
    token = context.args[0]
    user = update.effective_user
    msg = await update.message.reply_text("⌛ **Booting your clone...**")
    
    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app) 
        await app.initialize(); await app.start()
        me = await app.bot.get_me()
        add_cloned_bot(user.id, token, me.username, me.id)
        await msg.edit_text(f"✅ **Clone Ready!**\n\nBot: @{me.username}")
    except Exception as e:
        await msg.edit_text(f"❌ Error: `{e}`")

# =========================
# ⚙️ REGISTRATION
# =========================

def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    
    app.add_handler(CallbackQueryHandler(close_callback, pattern="close_msg"))
    app.add_handler(CallbackQueryHandler(clone_start_handler, pattern="back_start"))
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
