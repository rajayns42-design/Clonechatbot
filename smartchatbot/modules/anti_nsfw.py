from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
import time
from smartchatbot.config import LOGGER_GROUP  # Optional: aapka logger chat id

# ----------------------------
# ANTI-NSFW HANDLER
# ----------------------------
async def anti_nsfw_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user
    chat = update.effective_chat

    # Check for Media (Photo, Video, Sticker, GIF/Animation)
    is_media = (
        bool(update.message.photo) or
        bool(update.message.video) or
        bool(update.message.sticker) or
        bool(update.message.animation)
    )

    if not is_media:
        return  # Agar media nahi, kuch nahi karna

    try:
        # 1️⃣ Delete the NSFW message
        await update.message.delete()

        # 2️⃣ Restrict user for 24h
        mute_permissions = ChatPermissions(can_send_messages=False)
        until_ts = int(time.time() + 86400)  # 24 hours
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=user.id,
            permissions=mute_permissions,
            until_date=until_ts
        )

        # 3️⃣ Warning Message
        warn_text = (
            f"🚫 **Action Taken!**\n\n"
            f"User: {user.first_name}\n"
            "Reason: NSFW/18+ Media detected.\n"
            "Action: Message Deleted & User Muted for 24h 🤐"
        )
        await context.bot.send_message(chat_id=chat.id, text=warn_text, parse_mode="Markdown")

        # 4️⃣ Optional: Logger Group
        if LOGGER_GROUP:
            try:
                await context.bot.send_message(
                    chat_id=LOGGER_GROUP,
                    text=f"⚠️ NSFW Action\nChat: {chat.title} ({chat.id})\nUser: {user.first_name} ({user.id})\nTime: {time.ctime()}"
                )
            except:
                pass

    except Exception as e:
        print(f"Error in Anti-NSFW Handler: {e}")
