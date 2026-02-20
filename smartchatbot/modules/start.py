import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

# ==========================================
# ✶ FIXED ABSOLUTE IMPORTS
# ==========================================
from smartchatbot.config import Config
from smartchatbot.database import register_user
from smartchatbot.modules.logger import log_user_start

# Bot start time record
BOT_START_TIME = time.time()

def start_buttons(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⌯ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ⌯", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("🥀 Bᴏᴏᴋ", callback_data="help_menu"),
            InlineKeyboardButton("⌯ Hᴀʀɪ ⌯", url=f"https://t.me/{Config.OWNER_USERNAME.replace('@','')}")
        ],
        [
            InlineKeyboardButton("📨 Uᴩᴅᴀᴛᴇ", url=Config.UPDATE_CHANNEL),
            InlineKeyboardButton("📨 Sᴜᴩᴩᴏʀᴛ", url=Config.SUPPORT_GROUP)
        ]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    
    # 1. Database & Logger
    register_user(user.id, user.first_name, user.username)
    await log_user_start(update, context)

    # 2. Smart Photo Logic
    chat_photo = Config.START_IMG 
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            chat_photo = photos.photos[0][-1].file_id
    except:
        pass

    START_TEXT = (
        f"<blockquote>\n"
        f"𝖧𝖾𝗒 <a href='tg://user?id={user.id}'>{user.first_name}</a> ✨\n"
        f"I'ᴍ <b>{bot.first_name}</b>\n\n"
        "๏ 𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?\n"
        "➜ I'ᴍ A Sᴍᴀʀᴛ Aɪ Cʜᴀᴛ Aꜱꜱɪꜱᴛᴀɴᴛ\n"
        "➜ Hᴜᴍᴀɴ-Lɪᴋᴇ Rᴇᴩʟʏ\n\n"
        "๏ 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ?\n"
        "➜ Aᴅᴅ Mᴇ Bᴀʙʏ ʏᴏᴜʀ Gʀᴏᴜᴩ\n"
        "➜ Uꜱᴇ /Chatbot Oɴ ᴛᴏ Eɴᴀʙʟᴇ\n\n"
        "➜ Cʟɪᴄᴋ Tʜᴇ Hᴇʟᴩ Bᴜᴛᴛᴏɴ Fᴏʀ Mᴏʀᴇ 🫶\n"
        f"</blockquote>"
    )

    # 3. Callback (Button) vs Message (Command) Handling
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            # Media edit karega jab 'Back' dabayenge
            await query.edit_message_media(
                media=InputMediaPhoto(media=chat_photo, caption=START_TEXT, parse_mode="HTML"),
                reply_markup=start_buttons(bot.username)
            )
        except Exception:
            # Agar edit fail ho toh naya photo bhej dega
            await query.message.reply_photo(
                photo=chat_photo,
                caption=START_TEXT,
                reply_markup=start_buttons(bot.username),
                parse_mode="HTML"
            )
    else:
        # Seedha /start command ke liye
        await update.message.reply_photo(
            photo=chat_photo,
            caption=START_TEXT,
            reply_markup=start_buttons(bot.username),
            parse_mode="HTML"
        )

# =========================================
# ✶ HELP MENU & CALLBACKS
# =========================================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    help_text = (
        f"<blockquote>\n"
        "✨ <b>Hᴇᴩ Bᴏᴏᴋ</b> ✨\n\n"
        "👤 <b>User:</b> /start, /id\n"
        "⚙️ <b>Group:</b> /chatbot on | off\n\n"
        "➜ Mᴜʟᴛɪ Lᴀɴɢᴜᴀɢᴇ Sᴜᴩᴩᴏʀᴛ\n"
        "➜ Hᴜᴍᴀɴ-Lɪᴋᴇ Rᴇᴩʟʏ\n"
        f"</blockquote>"
    )

    back_button = [[InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="back_start")]]
    
    await query.edit_message_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(back_button),
        parse_mode="HTML"
    )

async def help_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # Yahan check ho raha hai kaunsa button daba
    if query.data == "back_start":
        await start(update, context)
    elif query.data == "help_menu":
        await help_menu(update, context)
