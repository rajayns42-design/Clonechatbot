import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from ..config import OWNER_ID
from ..database import get_all_users, remove_user # User remove agar bot block ho

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Owner Check
    if update.effective_user.id != int(OWNER_ID):
        return await update.message.reply_text("<blockquote>❌ <b>Sirf Owner hi broadcast kar sakta hai!</b></blockquote>", parse_mode="HTML")

    # 2. Reply Check
    if not update.message.reply_to_message:
        return await update.message.reply_text("<blockquote>📢 <b>Kissi message ko reply karein jise broadcast karna hai!</b></blockquote>", parse_mode="HTML")

    msg = await update.message.reply_text("🚀 <b>Broadcasting in progress...</b>", parse_mode="HTML")
    
    users = get_all_users()
    total_users = len(users)
    done = 0
    failed = 0
    blocked = 0
    
    for user_id in users:
        try:
            # Message copy karke bhej raha hai
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.reply_to_message.message_id
            )
            done += 1
            # Flood wait se bachne ke liye chota gap
            await asyncio.sleep(0.05) 
        except Exception as e:
            failed += 1
            # Agar user ne bot block kiya hai toh use DB se hata sakte ho (optional)
            # if "Forbidden" in str(e):
            #     remove_user(user_id)
            #     blocked += 1
            
    # Final Result Message
    final_text = (
        "✅ <b>BROADCAST FINISHED!</b>\n"
        f"<blockquote>\n"
        f"👤 <b>Total Users:</b> <code>{total_users}</code>\n"
        f"✔️ <b>Success:</b> <code>{done}</code>\n"
        f"❌ <b>Failed:</b> <code>{failed}</code>\n"
        f"</blockquote>\n"
        f"✨ <b>Task completed by:</b> {update.effective_user.first_name}"
    )
    
    await msg.edit_text(final_text, parse_mode="HTML")
