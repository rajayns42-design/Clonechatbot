from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
# Database imports (Relative path fixed for Heroku)
from ..database import set_welcome_status, get_welcome_status
from smartchatbot.config import START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL, OWNER_ID

# --- MASTER START (Profile Photo + Buttons Logic) ---
async def master_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Callback query aur normal message dono handle karega
    is_callback = bool(update.callback_query)
    user = update.effective_user
    bot = await context.bot.get_me()

    # User ki profile photo nikalne ka logic
    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        img = photos.photos[0][-1].file_id if photos.total_count > 0 else START_IMG
    except:
        img = START_IMG

    text = (
        f"Hey [ {user.first_name} ](tg://user?id={user.id}) ✨\n\n"
        f"I'm **{bot.first_name}** 🤖\n\n"
        "➜ **Smart AI Chat Assistant**\n"
        "➜ **Human like Hindi/English replies**\n"
        "➜ **Super Fast & 24/7 Online**\n\n"
        "**Add me to your group and use** `/chatbot on` ✅"
    )

    buttons = [
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("🛠 Help", callback_data="clone_help"),
            InlineKeyboardButton("👤 Owner", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ]
    ]

    if is_callback:
        await update.callback_query.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_photo(
            photo=img,
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )

# --- HELP CALLBACK ---
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    help_text = (
        "✨ **Smart AI Help Menu**\n\n"
        "🔹 `/chatbot on` — AI enable karein\n"
        "🔹 `/welcome on` — Welcome message chalu karein\n"
        "🔹 `/ping` — Speed check karein\n"
        "🔹 `/ban` / `/unban` — Admin power\n\n"
        "💬 **Just talk to me, I'll reply!**"
    )

    await query.message.edit_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]),
        parse_mode="Markdown"
    )

# --- Welcome Toggle ---
async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator']:
            return await update.message.reply_text("❌ Admin power chahiye iske liye!")
    except: return 

    if not context.args:
        return await update.message.reply_text("➜ Use: `/welcome on` or `/welcome off`?")

    action = context.args[0].lower()
    if action == "on":
        set_welcome_status(chat.id, True)
        await update.message.reply_text("✅ **Welcome Message ON!**")
    elif action == "off":
        set_welcome_status(chat.id, False)
        await update.message.reply_text("📴 **Welcome Message OFF!**")

# --- Welcome Member Action ---
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    chat_id = update.effective_chat.id
    if not get_welcome_status(chat_id):
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        welcome_text = f"Welcome **{member.first_name}** ✨ to the group!"
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
