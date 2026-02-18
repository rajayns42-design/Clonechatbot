import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================
# IMPORTS (adjust if needed)
# =========================

from smartchatbot.config import START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL
from modules.chatbot import chatbot_reply, chatbot_toggle
from modules.welcome import welcome_toggle, welcome_member


# =========================
# ANTI MEDIA DELETE
# =========================

async def anti_nsfw_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.effective_chat or not update.effective_user:
        return

    if update.effective_chat.type == "private":
        return

    try:
        member = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )

        if member.status in ["creator", "administrator"]:
            return

        if (
            update.message.photo
            or update.message.video
            or update.message.animation
            or update.message.sticker
        ):
            await update.message.delete()

            warn = await update.effective_chat.send_message(
                f"⚠️ {update.effective_user.first_name}, media not allowed!"
            )

            if context.job_queue:
                context.job_queue.run_once(
                    lambda c: warn.delete(),
                    5
                )

    except Exception as e:
        print("Anti media error:", e)


# =========================
# START MESSAGE
# =========================

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    bot_name = context.bot.first_name
    bot_owner_id = context.bot_data.get("owner_id", "123456")

    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        img = photos.photos[0][-1].file_id if photos.total_count else START_IMG
    except:
        img = START_IMG

    text = (
        f"Hey **{user.first_name}** ✨\n"
        f"I'm **{bot_name}**\n\n"
        "➜ Smart AI Chat Assistant\n"
        "➜ Human like replies\n"
        "➜ Fast response\n\n"
        "Use `/chatbot on` in group ✅"
    )

    buttons = [
        [InlineKeyboardButton(
            "➕ Add Me To Group",
            url=f"https://t.me/{context.bot.username}?startgroup=true"
        )],
        [
            InlineKeyboardButton("🛠 Help", callback_data="clone_help"),
            InlineKeyboardButton("👤 Owner", url=f"tg://user?id={bot_owner_id}")
        ],
        [
            InlineKeyboardButton("Updates", url=UPDATE_CHANNEL),
            InlineKeyboardButton("Support", url=SUPPORT_GROUP)
        ]
    ]

    await update.message.reply_photo(
        photo=img,
        caption=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )


# =========================
# HELP CALLBACK
# =========================

async def clone_help_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    await update.callback_query.message.reply_text(
        "Commands:\n"
        "/chatbot on — enable AI\n"
        "/welcome on — welcome msg\n"
        "Just talk — I reply 😄"
    )


# =========================
# PING
# =========================

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    start = time.time()
    m = await update.message.reply_text("🏓 Pong")
    ms = int((time.time() - start) * 1000)
    await m.edit_text(f"⚡ {ms} ms")


# =========================
# REGISTER HANDLERS
# =========================

def register_basic_handlers(app: Application):

    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("ping", ping_cmd))

    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    app.add_handler(CallbackQueryHandler(
        clone_help_cb,
        pattern="clone_help"
    ))

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chatbot_reply
    ))

    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome_member
    ))

    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL),
        anti_nsfw_delete
    ), group=1)
