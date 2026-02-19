import asyncio
import time

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
    OWNER_ID,
    LOGGER_GROUP,
    CLONE_LOGGER,
    START_IMG,
    SUPPORT_GROUP,
    UPDATE_CHANNEL
)

from ..database import (
    add_cloned_bot,
    remove_cloned_bot,
    users_collection,
    get_chat_status,
    set_chat_status
)

from .welcome import welcome_member
from .admin import ban_user, unban_user, mute_user, unmute_user
from .chatbot import chatbot_reply


# =========================
# 🔄 LOGGER SYSTEM
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    user = update.effective_user
    bot = await context.bot.get_me()

    text = (
        "👤 <b>NEW START</b>\n\n"
        f"🤖 Bot: {bot.first_name}\n"
        f"🆔 User: <code>{user.id}</code>\n"
        f"📝 Name: {user.first_name}\n"
        f"🏷 Username: @{user.username if user.username else 'N/A'}"
    )

    try:
        await context.bot.send_message(
            LOGGER_GROUP,
            text,
            parse_mode="HTML"
        )
    except:
        pass


# =========================
# ⚡ PING
# =========================

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("⚡")
    end = time.time()

    ms = round((end - start) * 1000, 2)

    await msg.edit_text(
        f"Pong — <code>{ms} ms</code>",
        parse_mode="HTML"
    )


# =========================
# 🌟 START HANDLER
# =========================

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()

    await log_user_start(update, context)

    # -------- owner lookup from clone db ----------
    clone_owner_id = OWNER_ID
    try:
        data = users_collection.find_one({"bot_id": bot.id})
        if data:
            clone_owner_id = data["owner_id"]
    except:
        pass

    owner_url = f"tg://user?id={clone_owner_id}"

    # -------- profile photo fallback ----------
    user_photo = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            user_photo = photos.photos[0][-1].file_id
    except:
        pass

    # -------- buttons ----------
    buttons = [
        [
            InlineKeyboardButton(
                "ADD ME BABY 💖",
                url=f"https://t.me/{bot.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("📢 UPDATE", url=UPDATE_CHANNEL),
            InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton("HELP 🛠", callback_data="back_start"),
            InlineKeyboardButton("OWNER 👑", url=owner_url)
        ]
    ]

    text = (
        f"Hey <a href='tg://user?id={user.id}'>{user.first_name}</a> ✨\n\n"
        f"I'm <b>{bot.first_name}</b> 🤖\n\n"

        "๏ <b>What Can I Do?</b>\n"
        "➜ Smart AI Assistant\n"
        "➜ Human-Like Conversations\n"
        "➜ Multi Language Support\n"
        "➜ Unlimited /Clone Features\n"
        "➜ 24x7 Fast Response\n\n"

        "๏ <b>How To Use Me?</b>\n"
        "➜ Add Me To Your Group\n"
        "➜ Use /chatbot on To Enable\n"
        "➜ Use /chatbot off To Disable\n\n"

        "➜ Click Help Button For More Commands 💜"
    )

    try:
        if update.message:
            await update.message.reply_photo(
                photo=user_photo,
                caption=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await update.callback_query.message.edit_caption(
                caption=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except:
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# =========================
# 🤖 CLONE SYSTEM
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

        # clone logger
        try:
            await context.bot.send_message(
                CLONE_LOGGER,
                f"🚀 Clone Created\nBot: @{me.username}\nOwner: {user.id}"
            )
        except:
            pass

        await msg.edit_text(f"Clone Ready: @{me.username}")

    except Exception as e:
        await msg.edit_text(f"Error: {e}")


# =========================
# ❌ CLOSE BUTTON
# =========================

async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()


# =========================
# ⚙️ REGISTER HANDLERS
# =========================

def register_all_handlers(app: Application):

    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("ping", ping_cmd))

    # admin
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))

    # callbacks
    app.add_handler(CallbackQueryHandler(close_callback, pattern="close_msg"))
    app.add_handler(CallbackQueryHandler(clone_start_handler, pattern="back_start"))

    # welcome
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member)
    )

    # chatbot
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply)
)
