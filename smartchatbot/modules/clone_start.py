import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL
from modules.chatbot import chatbot_reply, chatbot_toggle
from modules.welcome import welcome_toggle, welcome_member

# --- Anti-NSFW Logic (Sirf Delete karne ke liye) ---
async def anti_nsfw_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    # Check for Media (Photo, Video, GIF, Sticker)
    if (update.message.photo or update.message.video or 
        update.message.animation or update.message.sticker):
        
        try:
            # Automatic Delete
            await update.message.delete()
            
            # Optional: Chota sa alert message (aap ise hata bhi sakte hain)
            alert = await update.effective_chat.send_message("❌ NSFW/Media content deleted automatically!")
            # 5 second baad alert bhi delete ho jaye taaki group saaf rahe
            context.job_queue.run_once(lambda c: alert.delete(), 5)
        except Exception as e:
            print(f"Delete Error: {e}")

# --- Your Stylish Start Handler ---
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name 
    
    # Clone Owner ID (Default if not found)
    bot_owner_id = context.bot_data.get('owner_id', "654321") 

    # Profile Photo Logic
    try:
        user_photos = await context.bot.get_user_profile_photos(user.id)
        display_img = user_photos.photos[0][-1].file_id if user_photos.total_count > 0 else START_IMG
    except Exception:
        display_img = START_IMG

    welcome_text = (
        f"𝖧𝖾𝗒 {user.first_name}\n"
        f"𝖨'𝗆 **{bot_name}**\n\n"
        "๏ **𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?**\n"
        "➜ 𝖨’𝗆 𝖠 𝖲m𝖺𝗋𝗍 𝖠𝖨 𝖢𝗁𝖺𝗍 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍\n"
        "➜ 𝖧𝗎𝗆𝖺𝗇-𝖫𝗂𝗄𝖾 𝖢𝗈𝗇𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗈𝗇𝗌\n"
        "➜ 𝖬𝗎𝗅𝗍𝗂 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 𝖲𝗎𝗉𝗉𝗈𝗋𝗍\n"
        "➜ 𝟤𝟦𝗑𝟩 𝖥𝖺𝗌𝗍 𝖱𝖾𝗌𝗉𝗈𝗇𝗌𝖾\n\n"
        "๏ **𝗛𝗼𝘄 𝗧𝗼 𝗨𝘀𝗲 𝗠𝗲 ?**\n"
        "➜ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉\n"
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

# --- Clone Registration Logic ---
# Jab aap app.add_handler likhein, toh ye lines zaroor dalein:
# app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL, anti_nsfw_delete), group=1)
