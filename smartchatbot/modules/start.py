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

# ==========================================
# ✶ START LOGIC (Command + Callback)
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    
    # 1. Database me user register karna
    register_user(user.id, user.first_name, user.username)
    
    # 2. Logger group me update bhejna
    await log_user_start(update, context)

    # 3. Profile Photo fetch karna (Smart Logic)
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
        f"I'ᴍ <b>{bot.first_name}</b>\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅ \n"
        "๏ 𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?\n"
        "➜ I'ᴍ A Sᴍᴀʀᴛ Aɪ Cʜᴀᴛ Aꜱꜱɪꜱᴛᴀɴᴛ\n"
        "➜ Hᴜᴍᴀɴ-Lɪᴋᴇ Rᴇᴩʟʏ\n"
        "➜ Mᴜʟᴛɪ Lᴀɴɢᴜᴀɢᴇ Sᴜᴩᴩᴏʀᴛ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅ \n"
        "๏ 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ?\n"
        "➜ Aᴅᴅ Mᴇ Bᴀʙʏ ʏᴏᴜʀ Gʀᴏᴜᴩ\n"
        "➜ Uꜱᴇ /Chatbot Oɴ ᴛᴏ Eɴᴀʙʟᴇ\n"
        "➜ Uꜱᴇ /Chatbot σꜰꜰ ᴛᴏ Dɪꜱᴀʙʟᴇ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅ \n"
        "➜ Cʟɪᴄᴋ Tʜᴇ Hᴇʟᴩ Bᴜᴛᴛᴏɴ Fᴏʀ Mᴏʀᴇ 🫶\n"
        f"</blockquote>"
    )

    # Agar button dabakar pichle page par ja rahe hain (Back Button)
    if update.callback_query:
        query = update.callback_query
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=chat_photo, caption=START_TEXT, parse_mode="HTML"),
                reply_markup=start_buttons(bot.username)
            )
        except Exception:
            # Agar edit nahi ho paya toh naya photo bhej do
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
# ✶ HELP MENU LOGIC
# =========================================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Help text jo user ko dikhega
    help_text = (
        f"<blockquote>\n"
        "✨ <b>Hᴇᴩ Bᴏᴏᴋ</b> ✨\n\n"
        "👤 <b>User Commands:</b>\n"
        "• /start — Start the bot\n"
        "• /id — Get your info\n\n"
        "⚙️ <b>Group Settings:</b>\n"
        "• /chatbot on — AI Enable\n"
        "• /chatbot off — AI Disable\n\n"
        "➜ 24x7 Fᴀꜱᴛ Rᴇꜱᴩᴏɴꜱᴇ\n"
        f"</blockquote>"
    )

    back_button = [[InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="back_start")]]
    
    # Check karein ki command se khula hai ya button se
    if update.callback_query:
        await update.callback_query.edit_message_caption(
            caption=help_text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode="HTML"
        )
    else:
        # Agar koi /help type kare toh
        await update.message.reply_text(
            help_text, 
            reply_markup=InlineKeyboardMarkup(back_button), 
            parse_mode="HTML"
        )

# =========================================
# ✶ CALLBACK HANDLER (MAIN SWITCH)
# =========================================
async def help_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Button click ka response turant answer karein
    await query.answer()

    if query.data == "help_menu":
        await help_menu(update, context)
    elif query.data == "back_start":
        await start(update, context)
