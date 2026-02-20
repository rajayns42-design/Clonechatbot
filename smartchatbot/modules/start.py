import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    Application
)

from ..config import START_IMG, OWNER_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, OWNER_ID

# =========================
# START COMMAND (With DP)
# =========================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()

    # User Profile Photo Logic
    display_img = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            display_img = photos.photos[0][-1].file_id
    except:
        pass

    # Aapka Diya Hua Blockquote Text
    text = (
        f"<blockquote>\n"
        f"𝖧𝖾𝗒 <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
        f"I'ᴍ {bot.first_name}\n\n"
        "๏ 𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?\n"
        "➜ Sᴍᴀʀᴛ Aɪ Cʜᴀᴛᴛɪɴɢ Fᴇᴀᴛᴜʀᴇꜱ\n"
        "➜ Mᴜʟᴛɪ Lᴀɴɢᴜᴀɢᴇ Sᴜᴩᴩᴏʀᴛ Nᴏ Aʙᴜꜱᴇ\n"
        "➜ 24x7 Fᴀꜱᴛ Rᴇꜱᴩᴏɴꜱᴇ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅\n\n"
        "๏ <b>𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ?</b>\n"
        "➜ Aᴅᴅ Mᴇ Bᴀʙʏ ʏᴏᴜʀ Gʀᴏᴜᴩ\n"
        "➜ Uꜱᴇ /Chatbot On ᴛᴏ Eɴᴀʙʟᴇ\n"
        "➜ Uꜱᴇ /Chatbot Off ᴛᴏ Dɪꜱᴀʙʟᴇ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅\n\n"
        "➜ Cʟɪᴄᴋ Tʜᴇ Hᴇʟᴩ Bᴜᴛᴛᴏɴ Fᴏʀ Mᴏʀᴇ Cᴏᴍᴍᴀɴᴅꜱ 🫶\n"
        "</blockquote>"
    )

    buttons = [
        [InlineKeyboardButton("⌯ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ⌯", url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("🥀 Bᴏᴏᴋ", callback_data="help_menu"),
            InlineKeyboardButton("⌯ Hᴀʀɪ ⌯", url=f"https://t.me/{OWNER_USERNAME.replace('@','')}")
        ],
        [
            InlineKeyboardButton("📨Uᴩᴅᴀᴛᴇ", url=UPDATE_CHANNEL),
            InlineKeyboardButton("📨Sᴜᴩᴩᴏʀᴛ", url=SUPPORT_GROUP)
        ],
        [InlineKeyboardButton("🏓 Ping", callback_data="ping_btn")]
    ]

    if update.message:
        await update.message.reply_photo(photo=display_img, caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        try:
            await update.callback_query.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        except:
            await update.callback_query.message.reply_photo(photo=display_img, caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

# =========================
# PING HANDLER (With User DP)
# =========================

async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    start_time = time.time()
    
    # User DP for Ping
    user_photo = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            user_photo = photos.photos[0][-1].file_id
    except:
        pass

    msg = await update.message.reply_text("⚡")
    ping_ms = round((time.time() - start_time) * 1000, 3)
    
    # Screenshot wala Design
    text = (
        f"нᴇу <a href='tg://user?id={user.id}'>{user.first_name}</a> !!\n"
        f"╰─ <b>{bot.first_name}</b> 🍓 Is αℓινє 🥀 αη∂ ωᴏяᴋιηɢ\n"
        f"ғιηє ωιтн α ριηɢ ᴏғ\n"
        f"➡ <code>{ping_ms} ms</code>\n\n"
        f"мα∂є ву 💗 <a href='tg://user?id={OWNER_ID}'>𝐇𝐀𝐑𝐈</a> 🥀"
    )
    
    buttons = [
        [InlineKeyboardButton("⌯ Aᴅᴅ Mᴇ Bᴀʙʏ ⌯", url=f"https://t.me/{bot.username}?startgroup=true")],
        [InlineKeyboardButton("Cʟᴏꜱᴇ", callback_data="close_msg")]
    ]
    
    await msg.delete()
    await update.message.reply_photo(photo=user_photo, caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")

# =========================
# HELP MENU
# =========================

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    help_text = (
        "✨ <b>Hᴇᴩ Bᴏᴏᴋ</b> ✨\n\n"
        "👤 <b>User Commands:</b>\n"
        "• /start — Start bot\n"
        "• /ping — Check speed\n\n"
        "⚙️ <b>Group Settings:</b>\n"
        "• /chatbot on — Enable AI\n"
        "• /chatbot off — Disable AI\n"
    )
    back = [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
    await query.edit_message_caption(caption=help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(back))

# =========================
# UTILS
# =========================

async def close_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()

def register_start_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="help_menu"))
    app.add_handler(CallbackQueryHandler(start_command, pattern="start_back"))
    app.add_handler(CallbackQueryHandler(ping_handler, pattern="ping_btn"))
    app.add_handler(CallbackQueryHandler(close_msg, pattern="close_msg"))
