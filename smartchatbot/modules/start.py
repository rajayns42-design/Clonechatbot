import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..config import START_IMG, OWNER_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, OWNER_ID

# =========================
# START COMMAND (WITH NEW STYLE)
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot = await context.bot.get_me()

    # User Profile Photo Logic
    display_img = START_IMG
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            display_img = photos.photos[0][-1].file_id
    except:
        pass

    # Aapka Naya Blockquote Text
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

    # HTML parse mode zaroori hai blockquote ke liye
    if update.message:
        await update.message.reply_photo(
            photo=display_img, 
            caption=text, 
            parse_mode="HTML", 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        try:
            await update.callback_query.message.edit_caption(
                caption=text, 
                parse_mode="HTML", 
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            await update.callback_query.message.reply_photo(
                photo=display_img, 
                caption=text, 
                parse_mode="HTML", 
                reply_markup=InlineKeyboardMarkup(buttons)
            )

# ... Baki ping_handler aur help_callback wahi rahenge jo pehle the ...
