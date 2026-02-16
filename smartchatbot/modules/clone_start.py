from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name 
    
    # 1. Bot Owner ki ID nikalna (Jisne bot clone kiya hai)
    # Note: Aapke database me 'owner_id' save hona chahiye jab clone banta hai.
    # Yahan hum maan ke chal rahe hain aapne context me owner_id rakha hai ya config se aa raha hai.
    bot_owner_id = context.bot_data.get('owner_id', "Your_Default_Owner_ID")

    # 2. User ki Profile Photo
    try:
        user_photos = await context.bot.get_user_profile_photos(user.id)
        display_img = user_photos.photos[0][-1].file_id if user_photos.total_count > 0 else START_IMG
    except Exception:
        display_img = START_IMG

    # 3. Stylish Welcome Message
    welcome_text = (
        f"𝖧𝖾𝗒 {user.first_name}\n"
        f"𝖨'𝗆 **{bot_name}**\n\n"
        "๏ **𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?**\n"
        "➜ 𝖨’𝗆 𝖠 𝖲𝗆𝖺𝗋𝗍 𝖠𝖨 𝖢𝗁𝖺𝗍 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍\n"
        "➜ 𝖧𝗎𝗆𝖺𝗇-𝖫𝗂𝗄𝖾 𝖢𝗈𝗇𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗈𝗇𝗌\n"
        "➜ 𝖬𝗎𝗅𝗍𝗂 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 𝖲𝗎𝗉𝗉𝗈𝗋𝗍\n"
        "➜ 𝟤𝟦𝗑𝟩 𝖥𝖺𝗌𝗍 𝖱𝖾𝗌𝗉𝗈𝗇𝗌𝖾\n\n"
        "๏ **𝗛𝗼𝘄 𝗧𝗼 𝗨𝘀𝗲 𝗠𝗲 ?**\n"
        "➜ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉\n"
        "➜ 𝖴𝗌𝖾 `/chatbot on` 𝖳𝗈 𝖤𝗇𝖺𝖻𝗅𝖾\n"
        "➜ 𝖴𝗌𝖾 `/chatbot off` 𝖳𝗈 𝖣𝗂𝗌𝖺𝖻𝗅𝖾\n\n"
        "➜ 𝖢𝗅𝗂𝖼𝗄 𝖳𝗁𝖾 𝖧𝖾𝗅𝗉 𝖡𝗎𝗍𝗍𝗈𝗇 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 💜"
    )

    # 4. Buttons (With Dynamic Owner Link)
    buttons = [
        [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("🛠 Help", callback_data="clone_help"),
            # Is button pe click karne pe uski ID khulegi jisne clone banaya hai
            InlineKeyboardButton("👤 OWNER", url=f"tg://user?id={bot_owner_id}")
        ],
        [
            InlineKeyboardButton("🥀 Uᴩᴅᴀᴛᴇ", url=UPDATE_CHANNEL),
            InlineKeyboardButton("Sᴜᴩᴩᴏʀᴛ 🥀", url=SUPPORT_GROUP)
        ]
    ]

    await update.message.reply_photo(
        photo=display_img,
        caption=welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='Markdown'
    )
