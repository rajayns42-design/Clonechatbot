import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# Hamara wahi multi-api aur flirty logic import ho raha hai
from modules.chatbot import chatbot_reply, chatbot_toggle 
from config import API_ID, API_HASH

# Clone bots ko track karne ke liye cache
CLONES = {}

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("➜ **Token do na jaan!** `/clone [BOT_TOKEN]`")

    bot_token = context.args[0]
    await update.message.reply_text("🚀 **Processing...** Aapka unlimited flirty clone taiyar ho raha hai! ✨")

    try:
        # 1. Naya Bot Application Build karna
        # Yahan humne 'JobQueue' ko False rakha hai taki clones light-weight rahein
        app = Application.builder().token(bot_token).build()

        # 2. Saare Same Handlers Register karna (Unlimited Power)
        app.add_handler(CommandHandler("start", clone_start_handler))
        app.add_handler(CommandHandler("chatbot", chatbot_toggle)) # Group ON/OFF switch
        
        # Unlimited Reply Logic (Teno APIs: Gemini, Groq, Mistral)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

        # 3. Bot ko Background mein Polling par dalna
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        # Save clone in memory
        CLONES[user_id] = app
        
        await update.message.reply_text(
            "✅ **Mubarak ho baby!**\n\n"
            "Aapka clone bot ab redy.\n"
            "➜ Private mein unlimited chat karega.\n"
            "➜ Groups mein `/chatbot on` karke maze lo! 😉"
        )

    except Exception as e:
        print(f"Clone Error: {e}")
        await update.message.reply_text("❌ **Ofo!** Token galat hai ya Telegram ke nakhre hain. Phir se check karo!")

# --- Clone Bot Specific Start ---
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name
    
    # Ek real flirty welcome message clone bot ke liye
    welcome_msg = (
        f"𝖧𝖾𝗒 {user.first_name}! ✨\n"
        f"𝖨'𝗆 **{bot_name}**, tumhara naya flirty AI dost.\n\n"
        "➜ Mujhse private mein jitni chahe baatein karo, main kabhi nahi thakti! 💋\n"
        "➜ Mujhe apne groups mein add karo aur `/chatbot on` likho.\n\n"
        "**Chalo, ab kuch pyaari baatein shuru karein? 😉**"
    )
    
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')
