import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

# ==========================================
# ✶ FIXED ABSOLUTE IMPORTS (Heroku Fix)
# ==========================================
from smartchatbot.config import Config
from smartchatbot.database import register_user
from smartchatbot.modules.logging import log_user_start

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
    
    # Database me user save karna
    register_user(user.id, user.first_name, user.username)
    
    # Logger group me log bhejna
    await log_user_start(update, context)

    # Profile photo logic
    chat_photo = Config.START_IMG 
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            chat_photo = photos.photos[0][-1].file_id
    except Exception as e:
        print(f"Error fetching profile photo: {e}")

    # --- AAPKA NAYA BLOCKQUOTE TEXT ---
    START_TEXT = (
        f"<blockquote>\n"
        f"𝖧𝖾𝗒 <a href='tg://user?id={user.id}'>{user.first_name}</a> ✨\n"
        f"I'ᴍ <b>{bot.first_name}</b>\n\n"
        "๏ 𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?\n"
        "➜ I'ᴍ A Sᴍᴀʀᴛ Aɪ Cʜᴀᴛ Aꜱꜱɪꜱᴛᴀɴᴛ\n"
        "➜ Hᴜᴍᴀɴ-Lɪᴋᴇ Rᴇᴩʟʏ\n"
        "➜ Mᴜʟᴛɪ Lᴀɴɢᴜᴀɢᴇ Sᴜᴩᴩᴏʀᴛ Nᴏ Aʙᴜꜱᴇ\n\n"
        "➜ 24x7 Fᴀꜱᴛ Rᴇꜱᴩᴏɴꜱᴇ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅\n"
        "๏ 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ?\n"
        "➜ Aᴅᴅ Mᴇ Bᴀʙʏ ʏᴏᴜʀ Gʀᴏᴜᴩ\n"
        "➜ Uꜱᴇ /Chatbot Oɴ ᴛᴏ Eɴᴀʙʟᴇ\n"
        "➜ Uꜱᴇ /Chatbot Oꜰꜰ ᴛᴏ Dɪꜱᴀʙʟᴇ\n\n"
        "➜ Cʟɪᴄᴋ Tʜᴇ Hᴇʟᴩ Bᴜᴛᴛᴏɴ Fᴏʀ Mᴏʀᴇ Cᴏᴍᴍᴀɴᴅꜱ 🫶\n"
        f"</blockquote>"
    )

    if update.callback_query:
        try:
            await update.callback_query.message.edit_media(
                media=InputMediaPhoto(media=chat_photo, caption=START_TEXT, parse_mode="HTML"),
                reply_markup=start_buttons(bot.username)
            )
        except:
            await update.callback_query.message.reply_photo(
                photo=chat_photo,
                caption=START_TEXT,
                reply_markup=start_buttons(bot.username),
                parse_mode="HTML"
            )
    else:
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
        "👤 <b>User Commands:</b>\n"
        "• /start — Start the bot\n"
        "• /id — Get your info\n\n"
        "⚙️ <b>Group Settings:</b>\n"
        "• /chatbot on — AI Enable\n"
        "• /chatbot off — AI Disable\n"
        f"</blockquote>"
    )

    back = [[InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="back_start")]]
    await query.edit_message_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(back),
        parse_mode="HTML"
    )

async def help_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "back_start":
        await start(update, context)
    elif query.data == "help_menu":
        await help_menu(update, context)
