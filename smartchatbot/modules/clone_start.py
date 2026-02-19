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
# 🔄 LOGGER SYSTEM (Bite Fix)
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user: return
    user = update.effective_user
    bot = await context.bot.get_me()
    
    # HTML mode offset error fix karne ke liye sabse best hai
    text = (
        "👤 <b>NEW USER STARTED!</b>\n\n"
        f"🤖 <b>Bot Name:</b> {bot.first_name}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"📝 <b>Name:</b> {user.first_name}\n"
        f"🏷 <b>Username:</b> @{user.username if user.username else 'N/A'}"
    )
    try:
        await context.bot.send_message(chat_id=LOGGER_GROUP, text=text, parse_mode="HTML")
    except: pass

# =========================
# 🚀 PING & START HANDLERS
# =========================

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    bot = await context.bot.get_me()
    msg = await update.message.reply_text("⚡")
    
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    
    text = (
        f"нᴇу вαву!!\n"
        f"╰─ <b>{bot.first_name}</b> 🍓 Is αℓινє 🥀\n"
        f"ριηɢ: <code>{ping_ms} ms</code>\n\n"
        f"мα∂є ωιтн ❤️ ву <a href='tg://user?id={OWNER_ID}'>𝐇𝐀𝐑𝐈</a>"
    )
    
    buttons = [[InlineKeyboardButton("🗑 CLOSE", callback_data="close_msg")]]
    await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    
    # Logger update
    await log_user_start(update, context)

    # --- USER DP LOGIC ---
    user_photo = START_IMG # Default agar DP na ho
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            user_photo = photos.photos[0][-1].file_id
    except: pass

    # --- BUTTONS ---
    buttons = [
        [
            InlineKeyboardButton("𝐀𝐃𝐃 𝐌𝐄 𝐁𝐀𝐁𝐘 💖", url=f"https://t.me/{bot.username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 𝐔𝐏𝐃𝐀𝐓𝐄", url=UPDATE_CHANNEL),
            InlineKeyboardButton("💬 𝐒𝐔𝐏𝐏𝐎𝐑𝐓", url=SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton("𝐇𝐄𝐋𝐏 🛠", callback_data="clone_help"),
            InlineKeyboardButton("𝐇𝐀𝐑𝐈 👨‍💻", url=f"tg://user?id={OWNER_ID}")
        ]
    ]
    
    text = (
        f"нᴇу <a href='tg://user?id={user.id}'>{user.first_name}</a> ✨\n\n"
        f"I'm <b>{bot.first_name}</b> 🤖\n\n"
        "๏ <b>𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?</b>\n"
        "➜ 𝖨’𝗆 𝖠 𝖲𝗆𝖺𝗋𝗍 𝖠𝖨 𝖢𝗁𝖺𝗍 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍\n"
        "➜ 𝖧𝗎𝗆𝖺𝗇-𝖫𝗂ᴋ𝖾 𝖢𝗈𝗇𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗈𝗇𝗌\n"
        "➜ With Unlimited /Clone Features\n\n"
        "➜ <b>𝖢𝗅𝗂𝖼𝗄 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖡𝖾𝗅𝗈𝗐 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈</b> 💜"
    )

    try:
        if update.message:
            await update.message.reply_photo(
                photo=user_photo, 
                caption=text, 
                reply_markup=InlineKeyboardMarkup(buttons), 
                parse_mode="HTML"
            )
        else:
            await update.callback_query.message.edit_caption(
                caption=text, 
                reply_markup=InlineKeyboardMarkup(buttons), 
                parse_mode="HTML"
            )
    except:
        # Fallback agar photo bhejte waqt crash ho
        if update.message:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")

# =========================
# 🛠 CLONE & CALLBACKS
# =========================

async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: 
        return await update.message.reply_text("🚀 Usage: <code>/clone TOKEN</code>", parse_mode="HTML")
    
    token = context.args[0]
    user = update.effective_user
    msg = await update.message.reply_text("⌛ <b>Booting Clone...</b>", parse_mode="HTML")
    
    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app) 
        await app.initialize()
        await app.start()
        me = await app.bot.get_me()
        add_cloned_bot(user.id, token, me.username, me.id)
        await msg.edit_text(f"✅ <b>Clone Ready!</b>\n\nBot: @{me.username}", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Error: <code>{e}</code>", parse_mode="HTML")

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
