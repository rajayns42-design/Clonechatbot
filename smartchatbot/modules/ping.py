import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot ki speed check karne ke liye (Master aur Clones dono ke liye)"""
    
    # Message aane ka time note karein
    start_time = time.time()
    
    # Bot ka username nikalna taaki pata chale kaunsa clone reply kar raha hai
    bot_username = (await context.bot.get_me()).username
    
    # Temporary message
    sent_message = await update.message.reply_text(
        f"⚡ **Pinging @{bot_username}...**", 
        parse_mode="Markdown"
    )
    
    # Reply ke baad ka time
    end_time = time.time()
    
    # Latency in milliseconds
    ms = round((end_time - start_time) * 1000)
    
    # Close button
    keyboard = [[InlineKeyboardButton("🗑 Close", callback_data="close_ping")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Final result update karein
    await sent_message.edit_text(
        f"🚀 **Pong!**\n\n"
        f"👤 **Bot:** @{bot_username}\n"
        f"📡 **Latency:** `{ms}ms`\n"
        f"📶 **Status:** `Active`",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# Callback handler for Close button (Optional but good)
async def ping_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "close_ping":
        await query.message.delete()
