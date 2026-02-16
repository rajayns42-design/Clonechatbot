import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from modules.chatbot import chatbot_reply, chatbot_toggle 
from modules.welcome import welcome_toggle, welcome_member 
from database import add_cloned_bot # MongoDB function import
from config import API_ID, API_HASH

# Active clones in memory
CLONES = {}

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("➜ **Token do na jaan!** `/clone [BOT_TOKEN]`")

    bot_token = context.args[0]
    await update.message.reply_text("🚀 **Processing...** Aapka unlimited flirty clone taiyar ho raha hai! ✨")

    try:
        # 1. Naya Bot Application Build karna
        app = Application.builder().token(bot_token).build()

        # 2. Saare Handlers Register karna
        app.add_handler(CommandHandler("start", clone_start_handler))
        app.add_handler(CommandHandler("chatbot", chatbot_toggle))
        app.add_handler(CommandHandler("welcome", welcome_toggle))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

        # 3. Bot ko Start karna
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        # 4. MongoDB Cloud mein Save karna
        bot_info = await app.bot.get_me()
        add_cloned_bot(user_id, bot_token, bot_info.username)

        # Cache mein save karna
        CLONES[user_id] = app
        
        await update.message.reply_text(
            f"✅ **Mubarak ho baby!**\n\n"
            f"Aapka clone bot **@{bot_info.username}** ab Cloud mein save aur active hai.\n"
            f"➜ Restart ke baad bhi ye automatic on ho jayega.\n"
            f"➜ `/chatbot` aur `/welcome` dono switches ready hain! 😉"
        )

    except Exception as e:
        print(f"Clone Error: {e}")
        await update.message.reply_text("❌ **Ofo!** Token galat hai ya bot limit hit ho gayi hai.")

# --- Clone Bot Start Message (Dynamic) ---
async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name
    
    welcome_msg = (
        f"𝖧𝖾𝗒 {user.first_name} ✨\n"
        f"𝖨'𝗆 **{bot_name}**\n\n"
        f"๏ **𝗪𝗵𝗮𝘁 𝗖𝗮𝗻 𝗜 𝗗𝗼 ?**\n"
        f"➜ 𝖨’𝗆 𝖠 𝖲𝗆𝖺𝗋𝗍 𝖠𝖨 𝖢𝗁𝖺𝗍 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍\n"
        f"➜ 𝖧𝗎𝗆𝖺𝗇-𝖫𝗂𝗄𝖾 𝖢𝗈𝗇𝗏𝖾𝗋𝗌𝖺𝗍𝗂𝗈𝗇𝗌\n"
        f"➜ 𝖬𝗎𝗅𝗍𝗂 𝖫𝖺𝗇𝗀𝗎𝖺w𝖾 𝖲𝗎𝗉𝗉𝗈𝗋𝗍\n"
        f"➜ 𝖶𝗂𝗍𝗁 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 `/clone` 𝖥𝖾𝖺𝗍𝗎𝗋𝖾𝗌\n"
        f"➜ 𝟤𝟦𝗑𝟩 𝖥𝖺𝗌𝗍 𝖱𝖾𝗌𝗉𝗈𝗇𝗌𝖾\n\n"
        f"๏ **𝗛𝗼𝘄 𝗧𝗼 𝗨𝘀𝗲 𝗠𝗲 ?**\n"
        f"➜ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉\n"
        f"➜ 𝖴𝗌𝖾 `/chatbot on` 𝖳𝗈 𝖤𝗇𝖺𝖻𝗅𝖾\n"
        f"➜ 𝖴𝗌𝖾 `/chatbot off` 𝖳𝗈 𝖣𝗂𝗌𝖺𝖻𝗅𝖾\n\n"
        f"➜ 𝖢𝗅𝗂𝖼𝗄 𝖳𝗁𝖾 𝖧𝖾𝗅𝗉 𝖡𝗎𝗍𝗍𝗈𝗇 𝖥𝗈𝗋 𝖬𝗈𝗋𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 💜"
    )

    keyboard = [
        [InlineKeyboardButton("𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ➕", url=f"https://t.me/{context.bot.username}?startgroup=true")],
    ]
    
    await update.message.reply_text(welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
