import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID  # Ye aapki (Main Owner) ID hai

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check: Kya ye Main Owner hai?
    # Agar user_id config wali OWNER_ID se match nahi karti, toh bot reply tak nahi karega
    if user_id != int(OWNER_ID):
        return 

    # Check: Reply wala message hai ya nahi?
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ **Bhai, message pe reply karke `/broadcast` likho!**")
        return

    status_msg = await update.message.reply_text("🚀 **Main Owner Broadcast starting...**")
    
    # Database se saare users fetch karne ka logic (Example)
    # targets = await get_all_global_users() 
    targets = [1234567, 8901234] # Dummy IDs

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
            await asyncio.sleep(0.5) # Speed control
            
        except Exception:
            failed += 1
            continue

    await status_msg.edit_text(
        f"✅ **Global Broadcast Done!**\n\n"
        f"📤 **Sent:** `{success}`\n"
        f"❌ **Failed:** `{failed}`"
    )
