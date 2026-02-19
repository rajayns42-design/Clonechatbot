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
# IMPORTS
# =========================
from smartchatbot.config import START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL, OWNER_ID
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
                f"⚠️ {update.effective_user.first_name}, media not allowed here!"
            )
            
            # Warning delete after 5 seconds
            if context.job_queue:
                context.job_queue.run_once(lambda c: warn.delete(), 5)

    except Exception as e:
        print("Anti media error:", e)


# =========================
# START MESSAGE (Profile Photo + Buttons)
# =========================
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()

    # User ki profile photo nikalne ka logic
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            # Sabse latest profile photo (index 0)
            img = photos.photos[0][-1].file_id
        else:
            img = START_IMG
    except Exception:
        img = START_IMG

    # Start text with user link
    text = (
        f"Hey [ {user.first_name} ](tg://user?id={user.id}) ✨\n\n"
        f"I'm **{bot.first_name}** 🤖\n\n"
        "➜ **Smart AI Chat Assistant**\n"
        "➜ **Human like Hindi/English replies**\n"
        "➜ **Super Fast & 24/7 Online**\n\n"
        "**Add me to your group and use** `/chatbot on` ✅"
    )

    # Professional Buttons Layout
    buttons = [
        [
            InlineKeyboardButton(
                "➕ Add Me To Your Group",
                url=f"https://t.me/{bot.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("🛠 Help", callback_data="clone_help"),
            InlineKeyboardButton("👤 Owner", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
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
    query = update.callback_query
    await query.answer()

    help_text = (
        "✨ **Smart AI Help Menu**\n\n"
        "🔹 `/chatbot on` — Group mein AI enable karein\n"
        "🔹 `/chatbot off` — Group mein AI disable karein\n"
        "🔹 `/welcome on` — Welcome message chalu karein\n"
        "🔹 `/ping` — Bot ki current speed dekhein\n\n"
        "💬 **Mujhse baat karne ke liye bas message bhejien!**"
    )

    await query.message.edit_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="back_start")]
        ]),
        parse_mode="Markdown"
    )

# Back to Start Callback
async def back_start_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Yahan original start handler call ho jayega
    await clone_start_handler(update, context)


# =========================
# PING
# =========================
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    m = await update.message.reply_text("🏓 **Pinging...**", parse_mode="Markdown")
    ms = int((time.time() - start) * 1000)
    await m.edit_text(f"⚡ **Pong! Speed:** `{ms} ms`", parse_mode="Markdown")


# =========================
# REGISTER HANDLERS
# =========================
def register_basic_handlers(app: Application):
    # Commands
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    # Callbacks
    app.add_handler(CallbackQueryHandler(clone_help_cb, pattern="clone_help"))
    app.add_handler(CallbackQueryHandler(back_start_cb, pattern="back_start"))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # Anti-Media Handler (Group 1 for separate execution)
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL),
        anti_nsfw_delete
    ), group=1)
