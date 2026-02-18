from telegram import Update
from telegram.ext import ContextTypes
# FIXED: Relative import taaki Heroku par crash na ho
from ..database import set_welcome_status, get_welcome_status

# --- Welcome Toggle (Har bot aur har group ke liye alag) ---
async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # Admin Check: Sirf admins hi toggle kar sakte hain
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator']:
            return await update.message.reply_text("❌ Admin power chahiye iske liye!")
    except Exception:
        return 

    if not context.args:
        return await update.message.reply_text("➜ Use: `/welcome on` ya `/welcome off`?")

    action = context.args[0].lower()
    if action == "on":
        set_welcome_status(chat.id, True)
        await update.message.reply_text("✅ **Welcome Message ON!**")
    elif action == "off":
        set_welcome_status(chat.id, False)
        await update.message.reply_text("📴 **Welcome Message OFF!**")

# --- Clone Bot Welcome Action ---
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agar message nahi hai ya koi member join nahi kiya toh return
    if not update.message or not update.message.new_chat_members:
        return

    chat_id = update.effective_chat.id
    
    # Database se check karega ki is group mein welcome on hai ya nahi
    if not get_welcome_status(chat_id):
        return

    for member in update.message.new_chat_members:
        # Agar clone bot khud join kare toh welcome na kare
        if member.id == context.bot.id:
            continue
            
        first_name = member.first_name
        username = member.username
        
        # Formatting: Naam aur username ke saath
        if username:
            welcome_text = f"**{first_name}** (@{username}) ✨"
        else:
            welcome_text = f"**{first_name}** ✨"
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
