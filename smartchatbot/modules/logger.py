from telegram import Update
from telegram.ext import ContextTypes
from ..config import LOGGER_GROUP
import time

# =========================
# BOT DEPLOY/STARTUP LOG
# =========================
async def log_bot_on(context: ContextTypes.DEFAULT_TYPE):
    """Bot start hone par logger group me message bhejega"""
    if not LOGGER_GROUP:
        return

    bot_info = await context.bot.get_me()
    
    text = (
        f"🚀 <b>BOT DEPLOYED SUCCESSFULLY!</b>\n"
        f"<blockquote>\n"
        f"🤖 <b>Bot:</b> @{bot_info.username}\n"
        f"🆔 <b>ID:</b> <code>{bot_info.id}</code>\n"
        f"🛰️ <b>Status:</b> Online & Healthy ✅\n"
        f"⏰ <b>Time:</b> <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
        f"</blockquote>"
    )

    try:
        await context.bot.send_message(chat_id=int(LOGGER_GROUP), text=text, parse_mode="HTML")
    except Exception as e:
        print(f"Startup log error: {e}")

# =========================
# USER /START LOG
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not LOGGER_GROUP or not user:
        return

    photo_id = None
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            photo_id = photos.photos[0][-1].file_id
    except:
        pass

    text = (
        f"👤 <b>NEW USER STARTED!</b>\n"
        f"<blockquote>\n"
        f"📝 <b>Name:</b> {user.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"🏷 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
        f"</blockquote>"
    )

    try:
        if photo_id:
            await context.bot.send_photo(chat_id=int(LOGGER_GROUP), photo=photo_id, caption=text, parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=int(LOGGER_GROUP), text=text, parse_mode="HTML")
    except Exception as e:
        print(f"User log error: {e}")

# =========================
# BOT GROUP ADD LOG
# =========================
async def log_group_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.my_chat_member:
        return

    if update.my_chat_member.new_chat_member.status in ["member", "administrator"]:
        chat = update.effective_chat
        user = update.effective_user
        
        if not LOGGER_GROUP: return

        try:
            link = await chat.export_invite_link()
        except:
            link = "No Link"

        text = (
            f"🏰 <b>BOT ADDED TO GROUP!</b>\n"
            f"<blockquote>\n"
            f"👥 <b>Group:</b> {chat.title}\n"
            f"🆔 <b>G-ID:</b> <code>{chat.id}</code>\n"
            f"🔗 <b>Link:</b> {link}\n\n"
            f"👤 <b>Added By:</b> {user.first_name}\n"
            f"🆔 <b>U-ID:</b> <code>{user.id}</code>\n"
            f"</blockquote>"
        )

        try:
            await context.bot.send_message(chat_id=int(LOGGER_GROUP), text=text, parse_mode="HTML")
        except Exception as e:
            print(f"Group log error: {e}")
