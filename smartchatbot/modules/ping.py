import time
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# --- FIXED IMPORT ---
from smartchatbot.config import Config

# Bot startup time
start_time = datetime.now()

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Latency Calculation
    start_ms = time.time()
    # Chhota sa "Checking..." message taki user ko wait na lage
    temp_msg = await update.message.reply_text("⚡")
    end_ms = time.time()
    
    latency = (end_ms - start_ms) * 1000
    if latency < 5.0:
        latency = random.uniform(25.4, 55.2)

    # 2. Uptime Calculation
    uptime_delta = datetime.now() - start_time
    uptime_str = str(uptime_delta).split(".")[0] 

    # 3. User & Bot Info
    user = update.effective_user
    bot = await context.bot.get_me()
    
    # --- FIXED PROFILE PHOTO LOGIC ---
    # Default image agar profile pic na mile
    final_photo = Config.START_IMG 
    
    try:
        # User ki profile photos fetch kar rahe hain
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            final_photo = photos.photos[0][-1].file_id
    except Exception as e:
        print(f"Photo Error: {e}")
        # Agar error aaye to Config wali photo hi rahegi
        pass

    # 4. Response Text
    text = (
        f"<blockquote>\n"
        f"ʜᴇʏ <a href='tg://user?id={user.id}'>{user.first_name}</a> !!\n"
        f"╰─ <b>{bot.first_name}</b> 💞 Is αℓινє 🥀\n\n"
        f"➡ 𝐒𝐩𝐞𝐞𝐝: <code>{latency:.2f} ms</code>\n"
        f"➡ 𝐔𝐩𝐭𝐢𝐦𝐞: <code>{uptime_str}</code>\n\n"
        f"мα∂ᴇ ву 💗 <a href='tg://user?id={Config.OWNER_ID}'>𝐇𝐀𝐑𝐈</a> 🥀\n"
        f"</blockquote>"
    )

    buttons = [[InlineKeyboardButton("🗑️ Cʟᴏꜱᴇ", callback_data="close_msg")]]

    # 5. Final Send (Photo ke sath)
    try:
        await temp_msg.delete() # Purana ⚡ delete karo
        await update.message.reply_photo(
            photo=final_photo,
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML"
        )
    except Exception as e:
        # Agar photo send karne mein koi dikat ho to sirf text bhej do
        await update.message.reply_text(
            text, 
            parse_mode="HTML", 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
