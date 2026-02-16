from telegram import Update
from telegram.ext import ContextTypes
from database import set_welcome_status, get_welcome_status

# --- Welcome Toggle (On/Off) ---
async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # Admin Check
    member = await context.bot.get_chat_member(chat.id, user.id)
    if member.status not in ['administrator', 'creator']:
        return await update.message.reply_text("❌ Admin power chahiye iske liye!")

    if not context.args:
        return await update.message.reply_text("➜ `/welcome on` ya `/welcome off`?")

    action = context.args[0].lower()
    if action == "on":
        set_welcome_status(chat.id, True)
        await update.message.reply_text("✅ Welcome Message ON!")
    elif action == "off":
        set_welcome_status(chat.id, False)
        await update.message.reply_text("📴 Welcome Message OFF!")

# --- Name + Username Welcome Action ---
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not get_welcome_status(chat_id):
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
            
        first_name = member.first_name
        username = member.username
        
        # Check agar username hai ya nahi
        if username:
            welcome_text = f"**{first_name}** (@{username}) ✨"
        else:
            welcome_text = f"**{first_name}** ✨"
        
        # Sirf naam aur username jayega
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
