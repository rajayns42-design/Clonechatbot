from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .config import START_IMG, OWNER_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL

# --- Start Handler ---
async def master_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name 

    try:
        user_photos = await context.bot.get_user_profile_photos(user.id)
        display_img = user_photos.photos[0][-1].file_id if user_photos.total_count > 0 else START_IMG
    except:
        display_img = START_IMG

    welcome_text = (
        f"𝖧𝖾𝗒 {user.first_name}\n"
        f"𝖨'𝗆 **{bot_name}**\n\n"
        "๏ **𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?**\n"
        "➜ 𝖨 𝖢𝖺𝗇 𝖢𝗋𝖾𝖺𝗍𝖾 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖠𝖨 𝖢𝗅𝗈𝗇𝖾𝗌\n"
        "➜ 𝖧𝗎𝗆𝖺𝗇-𝖫𝗂𝗄𝖾 𝖢𝗈𝗇𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗈𝗇𝗌\n"
        "➜ 𝖬𝗎𝗅𝗍𝗂 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 𝖲𝗎𝗉𝗉𝗈𝗋𝗍\n\n"
        "➜ 𝖢𝗅𝗂𝖼𝗄 𝖳𝗁𝖾 𝖧𝖾𝗅𝗉 𝖡𝗎𝗍𝗍𝗈𝗇 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 💜"
    )

    buttons = [
        [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("🛠 Help", callback_data="help_back"), 
         InlineKeyboardButton("𝐇𝐀𝐑𝐈", url=f"https://t.me/{OWNER_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("🥀 Uᴩᴅᴀᴛᴇ", url=UPDATE_CHANNEL), InlineKeyboardButton("Sᴜᴩᴩᴏʀᴛ 🥀", url=SUPPORT_GROUP)]
    ]

    await update.message.reply_photo(
        photo=display_img,
        caption=welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='Markdown'
    )

# --- Help Callback Handler ---
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    help_text = (
        "✨ **𝖧𝖾𝗅𝗉 & 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌** ✨\n\n"
        "🤖 **𝖴𝗌𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**\n"
        "• `/start` - 𝖲𝗍𝖺𝗋𝗍 𝖳𝗁𝖾 𝖡𝗈𝗍\n"
        "• `/help` - 𝖦𝖾𝗍 𝖧𝖾𝗅𝗉 𝖬𝖾𝗇𝗎\n\n"
        "⚙️ **𝖦𝗋𝗈𝗎𝗉 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**\n"
        "• `/chatbot on` - 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝖨\n"
        "• `/chatbot off` - 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝖨\n\n"
        "🚀 **𝖢𝗅𝗈𝗇𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**\n"
        "• `/clone [token]` - 𝖢𝗋𝖾𝖺𝗍𝖾 𝖢𝗅𝗈𝗇𝖾\n"
        "• `/id` - 𝖦𝖾𝗍 𝖸𝗈𝗎𝗋 𝖨𝖣"
    )

    back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
    
    await query.edit_message_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(back_button),
        parse_mode='Markdown'
    )
