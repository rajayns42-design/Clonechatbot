import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..config import START_IMG, OWNER_ID

async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    
    # Latency calculate karne ke liye start time
    start_time = time.time()
    
    # 1. User ki profile photo fetch karna
    user_photo = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            user_photo = photos.photos[0][-1].file_id
    except:
        pass

    # 2. Speed check ke liye temporary animation
    msg = await update.message.reply_text("⚡")
    
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 3)
    
    # 3. Full Blockquote Text (HTML Mode)
    # 
    text = (
        f"<blockquote>\n"
        f"нᴇу <a href='tg://user?id={user.id}'>{user.first_name}</a> !!\n"
        f"╰─ <b>{bot.first_name}</b> 🍓 Is αℓινє 🥀 αη∂ ωᴏяᴋιηɢ\n"
        f"ғιηє ωιтн α ριηɢ ᴏғ\n"
        f"➡ <code>{ping_ms} ms</code>\n\n"
        f"мα∂є ву 💗 <a href='tg://user?id={OWNER_ID}'>𝐇𝐀𝐑𝐈</a> 🥀\n"
        f"</blockquote>"
    )
    
    # 4. Screenshot wale buttons
    buttons = [
        [
            InlineKeyboardButton("⌯ 𝐀ᴅᴅ Mᴇ Bᴀʙʏ ⌯", url=f"https://t.me/{bot.username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("🗑 ᴄʟᴏꜱᴇ", callback_data="close_ping")
        ]
    ]
    
    # 5. Purana message delete karke naya Photo + Blockquote Caption bhejega
    await msg.delete()
    await update.message.reply_photo(
        photo=user_photo, 
        caption=text, 
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )

# Close button handler
async def ping_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
