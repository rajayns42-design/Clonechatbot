from telegram import Update
from telegram.ext import ContextTypes
from ..config import LOGGER_GROUP

# =========================
# USER /START LOG
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not LOGGER_GROUP or not user:
        return

    # User ki profile photo fetch karna
    photo_id = None
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
    except:
        pass

    text = (
        "👤 <b>NEW USER STARTED!</b>\n\n"
        f"📝 <b>Name:</b> {user.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🏷 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
        f"🤖 <b>Bot:</b> @{(await context.bot.get_me()).username}"
    )

    try:
        if photo_id:
            await context.bot.send_photo(chat_id=int(LOGGER_GROUP), photo=photo_id, caption=text, parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=int(LOGGER_GROUP), text=text, parse_mode="HTML")
    except Exception as e:
        print(f"User start log error: {e}")


# =========================
# BOT GROUP ADD LOG
# =========================
async def log_group_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.my_chat_member:
        return

    # Check karna ki bot ko add kiya gaya
    if update.my_chat_member.new_chat_member.status == "member":
        chat = update.effective_chat
        user = update.effective_user  # Jisne bot ko add kiya
        if not LOGGER_GROUP:
            return

        # Group ka invite link nikalna (agar permissions ho)
        try:
            link = await chat.export_invite_link()
        except:
            link = "No Link (Admin Rights Missing)"

        text = (
            "🏰 <b>BOT ADDED TO NEW GROUP!</b>\n\n"
            f"👥 <b>Group Name:</b> {chat.title}\n"
            f"🆔 <b>Group ID:</b> <code>{chat.id}</code>\n"
            f"🔗 <b>Link:</b> {link}\n\n"
            f"👤 <b>Added By:</b> {user.first_name}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"🏷 <b>Username:</b> @{user.username if user.username else 'N/A'}"
        )

        try:
            await context.bot.send_message(chat_id=int(LOGGER_GROUP), text=text, parse_mode="HTML")
        except Exception as e:
            print(f"Group log error: {e}")
