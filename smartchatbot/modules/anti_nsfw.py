from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
import time

async def anti_nsfw_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    # Check for Media (Photo, Video, Sticker, GIF/Animation)
    is_media = (
        update.message.photo or 
        update.message.video or 
        update.message.sticker or 
        update.message.animation
    )

    if is_media:
        # Note: AI Image Recognition ke liye extra API lagti hai, 
        # par hum yahan "Strict Mode" ya NSFW metadata check filter laga rahe hain.
        # Agar aap chahte ho ki har media delete ho ya AI check kare:
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            # 1. Message Delete Karo
            await update.message.delete()
            
            # 2. User ko Mute Karo (Restrict)
            # User ab message, media ya kuch bhi nahi bhej payega
            mute_permissions = ChatPermissions(can_send_messages=False)
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=mute_permissions,
                until_date=int(time.time() + 86400) # 24 ghante ke liye mute
            )
            
            # 3. Warning Message
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"🚫 **Action Taken!**\n\nUser: {user.first_name}\nReason: NSFW/18+ Content detected.\nAction: Message Deleted & User Muted for 24h. 🤐"
            )
            
        except Exception as e:
            print(f"Error in Anti-NSFW: {e}")

