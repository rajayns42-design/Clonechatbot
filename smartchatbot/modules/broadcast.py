import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from smartchatbot.config import OWNER_ID
from smartchatbot.database import users_collection


# =========================
# GET ALL USERS FROM DB
# =========================

async def get_all_users():
    users = []
    async for u in users_collection.find({}, {"user_id": 1}):
        if "user_id" in u:
            users.append(u["user_id"])
    return users


# =========================
# OWNER ONLY BROADCAST
# =========================

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ✅ ONLY REAL OWNER — clone owner bhi allowed nahi
    if update.effective_user.id != int(OWNER_ID):
        return

    # ✅ reply check
    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "❌ Reply karke /broadcast use karo"
        )

    status_msg = await update.message.reply_text(
        "🚀 Broadcast starting..."
    )

    targets = await get_all_users()

    success = 0
    failed = 0

    for chat_id in targets:

        try:
            await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.reply_to_message.message_id
            )

            success += 1
            await asyncio.sleep(0.3)

        except Exception:
            failed += 1
            continue

    await status_msg.edit_text(
        f"✅ Broadcast Done\n\n"
        f"📤 Sent: {success}\n"
        f"❌ Failed: {failed}"
                           )
