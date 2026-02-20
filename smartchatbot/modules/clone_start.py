import time

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
# CONFIG
# =========================

from ..config import (
    OWNER_ID,
    LOGGER_GROUP,
    CLONE_LOGGER,
    START_IMG,
    SUPPORT_GROUP,
    UPDATE_CHANNEL
)

from ..database import (
    add_cloned_bot,
    users_collection,
)

from .welcome import welcome_member
from .admin import ban_user, unban_user, mute_user, unmute_user
from .chatbot import chatbot_reply


# =========================
# LOGGER
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.effective_user:
            return

        user = update.effective_user
        bot = await context.bot.get_me()

        text = (
            "👤 <b>NEW START</b>\n\n"
            f"🤖 Bot: {bot.first_name}\n"
            f"🆔 User: <code>{user.id}</code>\n"
            f"📝 {user.first_name}"
        )

        await context.bot.send_message(LOGGER_GROUP, text, parse_mode="HTML")

    except:
        pass


# =========================
# ⚡ STYLISH PING
# =========================

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    start = time.time()
    temp = await update.message.reply_text("⚡")

    ms = round((time.time() - start) * 1000, 3)
    bot = await context.bot.get_me()

    text = (
        "ʜᴇʏ ʙᴀʙʏ!!\n"
        f"<b>{bot.first_name}</b> is alive 🌹 and working fine\n"
        "WITH A PING OF\n"
        f"➥ <code>{ms} ms</code>\n\n"
        "ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ Aditya"
    )

    buttons = [
        [InlineKeyboardButton(
            "ADD ME BABY",
            url=f"https://t.me/{bot.username}?startgroup=true"
        )],
        [InlineKeyboardButton("CLOSE", callback_data="close_ping")]
    ]

    await temp.delete()

    await update.message.reply_photo(
        photo=START_IMG,
        caption=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def close_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()


async def ping_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # fake message wrapper so ping_cmd reuse ho sake
    update.message = update.callback_query.message
    await ping_cmd(update, context)


# =========================
# START (PROFILE PHOTO)
# =========================

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.callback_query:
        await update.callback_query.answer()

    user = update.effective_user
    bot = await context.bot.get_me()

    await log_user_start(update, context)

    owner_id = OWNER_ID
    data = users_collection.find_one({"bot_id": bot.id})
    if data:
        owner_id = data["owner_id"]

    owner_url = f"tg://user?id={owner_id}"

    # get user dp
    photo_id = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
    except:
        pass

    buttons = [
        [InlineKeyboardButton("➕ ADD ME", url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("📢 UPDATE", url=UPDATE_CHANNEL),
            InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton("🏓 PING", callback_data="ping_btn"),
            InlineKeyboardButton("👑 OWNER", url=owner_url)
        ]
    ]

    text = 
        text = f"""<blockquote>
𝖧𝖾𝗒 [{user.first_name}](tg://user?id={user.id})
I'ᴍ {bot_name}
────── ⋅ ⋅ ────── ⋅ ⋅ ⋅
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
    if update.message:
        await update.message.reply_photo(
            photo=photo_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        try:
            await update.callback_query.message.edit_caption(
                caption=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            await update.callback_query.message.reply_photo(
                photo=photo_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons)
            )


# =========================
# CLONE
# =========================

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        return await update.message.reply_text("Usage: /clone TOKEN")

    token = context.args[0]
    user = update.effective_user
    msg = await update.message.reply_text("Booting Clone...")

    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app)

        await app.initialize()
        await app.start()

        me = await app.bot.get_me()

        add_cloned_bot(user.id, token, me.username, me.id)

        await context.bot.send_message(
            CLONE_LOGGER,
            f"🚀 Clone Created\nBot: @{me.username}\nOwner: {user.id}"
        )

        await msg.edit_text(f"✅ Clone Ready: @{me.username}")

    except Exception as e:
        await msg.edit_text(f"❌ {e}")


# =========================
# REGISTER HANDLERS
# =========================

def register_all_handlers(app: Application):

    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("ping", ping_cmd))

    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))

    app.add_handler(CallbackQueryHandler(close_ping, pattern="close_ping"))
    app.add_handler(CallbackQueryHandler(ping_button, pattern="ping_btn"))

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member)
    )

    async def safe_chat(update, context):
        try:
            await chatbot_reply(update, context)
        except:
            pass

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, safe_chat)
                        )
