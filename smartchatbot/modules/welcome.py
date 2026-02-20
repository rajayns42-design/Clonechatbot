from telegram import Update
from telegram.ext import ContextTypes
# Database imports
from ..database import set_welcome_status, get_welcome_status

# =========================
# WELCOME TOGGLE (ADMIN ONLY)
# =========================
async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator']:
            return await update.message.reply_text("❌ Admin power chahiye iske liye!")
    except: return 

    if not context.args:
        return await update.message.reply_text("➜ Use: `/welcome on` or `/welcome off`?")

    action = context.args[0].lower()
    if action == "on":
        set_welcome_status(chat.id, True)
        await update.message.reply_text("✅ Welcome messages ON!")
    elif action == "off":
        set_welcome_status(chat.id, False)
        await update.message.reply_text("📴 Welcome messages OFF!")

# =========================
# WELCOME NEW MEMBER
# =========================
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    chat_id = update.effective_chat.id
    if not get_welcome_status(chat_id):
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        # Username ya First name
        username = f"@{member.username}" if member.username else member.first_name
        await update.message.reply_text(f"Welcome {username} 🎉")
