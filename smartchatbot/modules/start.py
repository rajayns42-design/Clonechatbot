from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    Application
)

from .config import START_IMG, OWNER_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL


# =========================
# START HANDLER
# =========================

async def master_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()

    # ---------- USER PROFILE PHOTO ----------
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            display_img = photos.photos[0][-1].file_id
        else:
            display_img = START_IMG
    except:
        display_img = START_IMG

    # ---------- TEXT ----------
        text = f"""<blockquote>
𝖧𝖾𝗒 [{user.first_name}](tg://user?id={user.id})
I'ᴍ {bot_name}

๏ 𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?
➜ Wɪᴛʜ Aɪ /Cʟᴏɴᴇ's Fᴇᴀᴛᴜʀᴇꜱ
➜ Mᴜʟᴛɪ Lᴀɴɢᴜᴀɢᴇ Sᴜᴩᴩᴏʀᴛ Nᴏ Aʙᴜꜱᴇ
➜ 24x7 Fᴀꜱᴛ Rᴇꜱᴩᴏɴꜱᴇ
────── ⋅ ⋅ ────── ⋅ ⋅ ⋅

๏ 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ?
➜ Aᴅᴅ Mᴇ Bᴀʙʏ ʏᴏᴜʀ Gʀᴏᴜᴩ
➜ Uꜱᴇ /Chatbot On ᴛᴏ Eɴᴀʙʟᴇ
➜ Uꜱᴇ /Chatbot Off ᴛᴏ Dɪꜱᴀʙʟᴇ
────── ⋅ ⋅ ────── ⋅ ⋅ ⋅

➜ Cʟɪᴄᴋ Tʜᴇ Hᴇʟᴩ Bᴜᴛᴛᴏɴ Fᴏʀ Mᴏʀᴇ Cᴏᴍᴍᴀɴᴅꜱ 🫶
</blockquote>"""
    )

    # ---------- BUTTONS ----------
    buttons = [
        [
            InlineKeyboardButton(
                "➕ ADD ME",
                url=f"https://t.me/{bot.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("🛠 Help", callback_data="help_menu"),
            InlineKeyboardButton(
                "👑 Owner",
                url=f"https://t.me/{OWNER_USERNAME.replace('@','')}"
            )
        ],
        [
            InlineKeyboardButton("📢 Update", url=UPDATE_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton("🏓 Ping", callback_data="ping_btn")
        ]
    ]

    # ---------- SEND ----------
    if update.message:
        await update.message.reply_photo(
            photo=display_img,
            caption=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.callback_query.message.reply_photo(
            photo=display_img,
            caption=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# =========================
# HELP MENU
# =========================

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    help_text = (
        "✨ **HELP MENU** ✨\n\n"
        "👤 User Commands:\n"
        "/start — Start bot\n"
        "/ping — Check speed\n\n"
        "🤖 Clone:\n"
        "/clone TOKEN — Create clone\n\n"
        "⚙️ Group:\n"
        "/chatbot on/off"
    )

    back = [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]

    await query.edit_message_caption(
        caption=help_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(back)
    )


# =========================
# PING BUTTON
# =========================

import time

async def ping_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    start = time.time()
    ms = round((time.time() - start) * 1000, 2)

    btn = [[InlineKeyboardButton("❌ Close", callback_data="close_ping")]]

    await query.edit_message_caption(
        caption=f"🏓 Pong!\n⚡ Speed: `{ms} ms`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btn)
    )


async def close_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()


# =========================
# REGISTER HANDLERS
# =========================

def register_start_handlers(app: Application):

    app.add_handler(CommandHandler("start", master_start))

    app.add_handler(CallbackQueryHandler(help_callback, pattern="help_menu"))
    app.add_handler(CallbackQueryHandler(master_start, pattern="start_back"))
    app.add_handler(CallbackQueryHandler(ping_button, pattern="ping_btn"))
    app.add_handler(CallbackQueryHandler(close_ping, pattern="close_ping"))
