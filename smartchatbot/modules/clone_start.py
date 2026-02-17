import time  # Fix: 'I' small rahega
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# In modules ko check kar lena ki filenames sahi hain
from smartchatbot.config import START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL
from modules.chatbot import chatbot_reply, chatbot_toggle
from modules.welcome import welcome_toggle, welcome_member

# --- Fixed Anti-Media Logic ---
async def anti_nsfw_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Basic Checks
    if not update.message or not update.effective_chat or not update.effective_user:
        return

    # Check if Private Chat (Private mein delete nahi karna chahiye)
    if update.effective_chat.type == "private":
        return

    try:
        # 1. Check if User is Admin (Admins can send media)
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        member = await context.bot.get_chat_member(chat_id, user_id)
        
        if member.status in ['creator', 'administrator']:
            return 

        # 2. Check for Media (Photo, Video, GIF, Sticker)
        if (update.message.photo or update.message.video or 
            update.message.animation or update.message.sticker):
            
            # Message Delete karo
            await update.message.delete()
            
            # Alert message bhejo (Sirf user ko batane ke liye)
            alert = await update.effective_chat.send_message(
                f"⚠️ {update.effective_user.first_name}, media messages are not allowed in this group!"
            )
            
            # 5 second baad alert delete ho jaye (Group saaf rakhne ke liye)
            # Make sure you have job_queue enabled in your Application
            context.job_queue.run_once(lambda c: alert.delete(), 5)

    except Exception as e:
        print(f"Anti-Media Error: {e}")

# --- Your Stylish Start Handler (Fixed) ---
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name 
    
    # Clone Owner ID Logic
    bot_owner_id = context.bot_data.get('owner_id', "654321") 

    # Profile Photo Logic (Error proof)
    try:
        user_photos = await context.bot.get_user_profile_photos(user.id)
        display_img = user_photos.photos[0][-1].file_id if user_photos.total_count > 0 else START_IMG
    except Exception:
        display_img = START_IMG

    welcome_text = (
        f"𝖧𝖾y **{user.first_name}**\n"
        f"𝖨'𝗆 **{bot_name}**\n\n"
        "๏ **𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?**\n"
        "➜ 𝖨’𝗆 𝖠 𝖲m𝖺𝗋𝗍 𝖠𝖨 𝖢𝗁𝖺𝗍 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍\n"
        "➜ 𝖧𝗎𝗆𝖺𝗇-𝖫𝗂𝗄𝖾 𝖢𝗈𝗇𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗈𝗇𝗌\n"
        "➜ 𝖬𝗎𝗅𝗍𝗂 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 𝖲𝗎𝗉𝗉𝗈𝗋𝗍\n"
        "➜ 𝟤𝟦𝗑𝟩 𝖥𝖺𝗌𝗍 𝖱𝖾𝗌𝗉𝗈𝗇𝗌𝖾\n\n"
        "๏ **𝗛𝗼𝘄 𝗧𝗼 𝗨𝘀𝗲 𝗠𝗲 ?**\n"
        "➜ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎 r 𝖦𝗋𝗈𝗎𝗉\n"
        "➜ 𝖴𝗌𝖾 `/chatbot on` 𝖳𝗈 𝖤𝗇𝖺𝖻𝗅𝖾\n\n"
        "➜ 𝖢𝗅𝗂𝖼𝗄 𝖳𝗁𝖾 𝖧𝖾𝗅𝗉 𝖡𝗎𝗍𝗍𝗈𝗇 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 💜"
    )

    buttons = [
        [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("🛠 Help", callback_data="clone_help"),
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
