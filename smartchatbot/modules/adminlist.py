from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

async def get_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Private chat mein admin list ki zarurat nahi
    if update.effective_chat.type == "private":
        return await update.message.reply_text("❌ Ye command sirf groups mein kaam karti hai!")

    status_msg = await update.message.reply_text("🔍 **Admins ki list nikaal raha hoon...**")

    try:
        # Bot us group ke saare admins ki list nikalega
        admins = await context.bot.get_chat_administrators(chat_id)
        
        admin_text = f"👮 **Admin List for {update.effective_chat.title}:**\n\n"
        
        owner_text = ""
        admins_text = ""

        for admin in admins:
            user = admin.user
            # Name setup (agar username nahi hai toh first name)
            mention = user.mention_markdown_v2()
            
            if admin.status == ChatMemberStatus.OWNER:
                owner_text = f"👑 **Owner:**\n└ {mention}\n\n"
            else:
                admins_text += f"├ {mention}\n"

        # Text formatting
        if not admins_text:
            admins_text = "└ No other admins found."
        else:
            # Last character ko fix karne ke liye
            admins_text = "✨ **Admins:**\n" + admins_text[:-1].replace("├", "└", 1) if "├" in admins_text else admins_text

        full_message = f"{admin_text}{owner_text}{admins_text}"
        
        await status_msg.edit_text(full_message, parse_mode='MarkdownV2')

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {e}")
