import time
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.config import Config
from bot.database import register_user
from bot.logging import log_user_start

# Bot start time record
BOT_START_TIME = time.time()

def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "d"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0: break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    time_list.reverse()
    return ":".join(time_list)

def start_buttons(bot_username):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⌯ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ⌯", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("🥀 Bᴏᴏᴋ", callback_data="help_menu"),
            InlineKeyboardButton("⌯ Hᴀʀɪ ⌯", url=f"https://t.me/{Config.OWNER_USERNAME.replace('@','')}")
        ],
        [
            InlineKeyboardButton("📨 Uᴩᴅᴀᴛᴇ", url=Config.UPDATES_CHANNEL),
            InlineKeyboardButton("📨 Sᴜᴩᴩᴏʀᴛ", url=Config.SUPPORT_CHAT)
        ]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()
    
    # DB and Logging
    await register_user(user.id, user.first_name, user.username)
    await log_user_start(update, context)

    # Naya Start Text with Full Blockquote
    START_TEXT = (
        f"<blockquote>\n"
        f"𝖧𝖾𝗒 <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
        f"I'ᴍ <b>{bot.first_name}</b>\n\n"
        "๏ 𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?\n"
        "➜ I'ᴍ A Sᴍᴀʀᴛ Aɪ Cʜᴀᴛ Aꜱꜱɪꜱᴛᴀɴᴛ\n"
        "➜ Hᴜᴍᴀɴ-Lɪᴋᴇ Rᴇᴩʟʏ\n"
        "➜ Mᴜʟᴛɪ Lᴀɴɢᴜᴀɢᴇ Sᴜᴩᴩᴏʀᴛ Nᴏ Aʙᴜꜱᴇ\n\n"
        "➜ 24x7 Fᴀꜱᴛ Rᴇꜱᴩᴏɴꜱᴇ\n"
        "────── ⋅ ⋅ ────── ⋅ ⋅ ⋅\n"
        "๏ <b>𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘 ?</b>\n"
        "➜ Aᴅᴅ Mᴇ Bᴀʙʏ ʏᴏᴜʀ Gʀᴏᴜᴩ\n"
        "➜ Uꜱᴇ /Chatbot Oɴ ᴛᴏ Eɴᴀʙʟᴇ\n"
        "➜ Uꜱᴇ /Chatbot Oꜰꜰ ᴛᴏ Dɪꜱᴀʙʟᴇ\n\n"
        "➜ Cʟɪᴄᴋ Tʜᴇ Hᴇʟᴩ Bᴜᴛᴛᴏɴ Fᴏʀ Mᴏʀᴇ Cᴏᴍᴍᴀɴᴅꜱ 🫶\n"
        f"</blockquote>"
    )

    if update.message:
        await update.message.reply_photo(
            photo=Config.START_IMG,
            caption=START_TEXT,
            reply_markup=start_buttons(bot.username),
            parse_mode="HTML"
        )
    else:
        await update.callback_query.message.edit_caption(
            caption=START_TEXT,
            reply_markup=start_buttons(bot.username),
            parse_mode="HTML"
        )

# =========================================
# ✶ HELP MENU (Full Blockquote)
# =========================================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    help_text = (
        f"<blockquote>\n"
        "✨ <b>Hᴇᴩ Bᴏᴏᴋ</b> ✨\n\n"
        "👤 <b>User Commands:</b>\n"
        "• /start — Start the bot\n"
        "• /ping — Check latency\n\n"
        "⚙️ <b>Group Settings:</b>\n"
        "• /chatbot on — Enable AI\n"
        "• /chatbot off — Disable AI\n"
        f"</blockquote>"
    )

    back = [[InlineKeyboardButton("⬅️ Bᴀᴄᴋ", callback_data="back_start")]]

    await query.edit_message_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(back),
        parse_mode="HTML"
    )

# =========================================
# ✶ CALLBACK HANDLER
# =========================================
async def help_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back_start":
        await start(update, context)
    elif data == "help_menu":
        await help_menu(update, context)
