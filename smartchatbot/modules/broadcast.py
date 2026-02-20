import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from ..config import OWNER_ID
from ..database import get_all_users # Maan ke chalte hain ye function sabhi user IDs deta hai

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sirf Owner broadcast kar sakta hai
    if update.effective_user.id != int(OWNER_ID):
        return await update.message.reply_text("❌ <b>Sirf Owner hi broadcast kar sakta hai!</b>", parse_mode="HTML")

    if not update.message.reply_to_message:
        return await update.message.reply_text("📢 <b>Kissi message ko reply karein jise broadcast karna hai!</b>", parse_mode="HTML")

    msg = await update.message.reply_text("🚀 <b>Broadcast shuru ho raha hai...</b>", parse_mode="HTML")
    
    users = get_all_users() # Database se list
    done = 0
    failed = 0
    
    for user_id in users:
        try:
            # Reply wala message copy karke bhejega
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.reply_to_message.message_id
            )
            done += 1
            await asyncio.sleep(0.1) # Flood wait se bachne ke liye
        except:
            failed += 1
            
    await msg.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"👤 <b>Total Users:</b> <code>{len(users)}</code>\n"
        f"✔️ <b>Success:</b> <code>{done}</code>\n"
        f"❌ <b>Failed:</b> <code>{failed}</code>",
        parse_mode="HTML"
    )
