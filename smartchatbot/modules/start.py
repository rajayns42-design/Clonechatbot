import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..config import START_IMG, OWNER_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, OWNER_ID

# =========================
# START COMMAND (WITH PROFILE PIC)
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()

    display_img = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            display_img = photos.photos[0][-1].file_id
    except:
        pass

    text = (
        f"<blockquote>\n"
        f"𝖧𝖾𝗒 <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
        f"I'ᴍ {bot.first_name}\n\n"
        "๏ 𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?\n"
        "➜ I'ᴍ A Sᴍᴀʀᴛ Aɪ Cʜᴀᴛ Aꜱꜱɪꜱᴛᴀɴᴛ\n"
        "➜ 24x7 Fᴀꜱᴛ Rᴇꜱᴩᴏɴꜱᴇ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅\n"
        "➜ Cʟɪᴄᴋ Tʜᴇ Hᴇʟᴩ Bᴜᴛᴛᴏɴ Fᴏʀ Mᴏʀᴇ Cᴏᴍᴍᴀɴᴅꜱ 🫶\n"
        "</blockquote>"
    )

    buttons = [
        [InlineKeyboardButton("⌯ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ⌯", url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("🥀 Bᴏᴏᴋ", callback_data="help_menu"),
            InlineKeyboardButton("⌯ Hᴀʀɪ ⌯", url=f"https://t.me/{OWNER_USERNAME.replace('@','')}")
        ],
        [
            InlineKeyboardButton("📨Uᴩᴅᴀᴛᴇ", url=UPDATE_CHANNEL),
            InlineKeyboardButton("📨Sᴜᴩᴩᴏʀᴛ", url=SUPPORT_GROUP)
        ],
        [InlineKeyboardButton("🏓 Ping", callback_data="ping_btn")]
    ]

    if update.message:
        await update.message.reply_photo(photo=display_img, caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        except:
            await update.callback_query.message.reply_photo(photo=display_img, caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

# =========================
# HELP & PING HANDLERS
# =========================
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query: await query.answer()

    help_text = (
        "✨ <b>Hᴇᴩ Bᴏᴏᴋ</b> ✨\n\n"
        "👤 <b>Commands:</b>\n"
        "• /start — Start bot\n"
        "• /ping — Check speed\n"
        "• /chatbot on/off — Enable AI\n"
    )
    back = [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
    await query.edit_message_caption(caption=help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(back))

async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    user = update.effective_user
    
    if update.callback_query:
        await update.callback_query.answer("Checking...")
        msg = await update.callback_query.message.reply_text("⚡")
    else:
        msg = await update.message.reply_text("⚡")
        
    ping_ms = round((time.time() - start_time) * 1000, 3)
    text = f"<blockquote>нᴇу {user.first_name}!!\n➡ <code>{ping_ms} ms</code></blockquote>"
    
    user_photo = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0: user_photo = photos.photos[0][-1].file_id
    except: pass

    await msg.delete()
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=user_photo,
        caption=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 Close", callback_data="close_ping")]])
    )

# MISSING HANDLER FIXED
async def ping_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.delete()

async def close_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.delete()
