import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..config import START_IMG, OWNER_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, OWNER_ID

# =========================
# START COMMAND (FIXED)
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
        "➜ Hᴜᴍᴀɴ-Lɪᴋᴇ Rᴇᴩʟʏ\n"
        "➜ Mᴜʟᴛɪ Lᴀɴɢᴜᴀɢᴇ Sᴜᴩᴩᴏʀᴛ Nᴏ Aʙᴜꜱᴇ\n\n"
        "➜ 24x7 Fᴀꜱᴛ Rᴇꜱᴩᴏɴꜱᴇ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅\n"
        "๏ <b>𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ?</b>\n"
        "➜ Aᴅᴅ Mᴇ Bᴀʙʏ ʏᴏᴜʀ Gʀᴏᴜᴩ\n"
        "➜ Uꜱᴇ /Chatbot On ᴛᴏ Eɴᴀʙʟᴇ\n"
        "➜ Uꜱᴇ /Chatbot Off ᴛᴏ Dɪꜱᴀʙʟᴇ\n\n"
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
    else:
        try:
            await update.callback_query.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        except:
            await update.callback_query.message.reply_photo(photo=display_img, caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

# =========================
# HELP CALLBACK (MISSING IN YOUR LAST CODE)
# =========================
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    help_text = (
        "✨ <b>Hᴇᴩ Bᴏᴏᴋ</b> ✨\n\n"
        "👤 <b>User Commands:</b>\n"
        "• /start — Start bot\n"
        "• /ping — Check speed\n\n"
        "⚙️ <b>Group Settings:</b>\n"
        "• /chatbot on — Enable AI\n"
        "• /chatbot off — Disable AI\n"
    )
    back = [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
    
    if query:
        await query.edit_message_caption(caption=help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(back))
    else:
        await update.message.reply_text(help_text, parse_mode="HTML")

# =========================
# PING HANDLER
# =========================
async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    start_time = time.time()
    
    msg = await update.message.reply_text("⚡")
    ping_ms = round((time.time() - start_time) * 1000, 3)
    
    text = (
        f"нᴇу <a href='tg://user?id={user.id}'>{user.first_name}</a> !!\n"
        f"╰─ <b>{bot.first_name}</b> 🍓 Is αℓινє 🥀 αη∂ ωᴏяᴋιηɢ\n"
        f"ғιηє ωιтн α ριηɢ ᴏғ\n"
        f"➡ <code>{ping_ms} ms</code>\n\n"
        f"мα∂є ву 💗 <a href='tg://user?id={OWNER_ID}'>𝐇𝐀𝐑𝐈</a> 🥀"
    )
    
    buttons = [[InlineKeyboardButton("Cʟᴏꜱᴇ", callback_data="close_msg")]]
    await msg.delete()
    await update.message.reply_photo(photo=START_IMG, caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")

async def close_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()
