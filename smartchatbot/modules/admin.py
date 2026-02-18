from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

# --- HELPER: Admin Check karne ke liye ---
async def is_admin(update: Update):
    """Check karta hai ki command chalane wala admin hai ya nahi"""
    user_status = (await update.effective_chat.get_member(update.effective_user.id)).status
    return user_status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]

# --- 1. ADMIN LIST ---
async def get_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if update.effective_chat.type == "private":
        return await update.message.reply_text("❌ Ye command sirf groups mein kaam karti hai!")

    status_msg = await update.message.reply_text("🔍 **Admins ki list nikaal raha hoon...**")

    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        admin_text = f"👮 **Admin List for {update.effective_chat.title}:**\n\n"
        
        owner_text = ""
        admins_text = ""

        for admin in admins:
            user = admin.user
            mention = user.mention_markdown_v2()
            
            if admin.status == ChatMemberStatus.OWNER:
                owner_text = f"👑 **Owner:**\n└ {mention}\n\n"
            else:
                admins_text += f"├ {mention}\n"

        if not admins_text:
            admins_text = "└ No other admins found."
        else:
            admins_text = "✨ **Admins:**\n" + admins_text[:-1].replace("├", "└", 1) if "├" in admins_text else admins_text

        full_message = f"{admin_text}{owner_text}{admins_text}"
        await status_msg.edit_text(full_message, parse_mode='MarkdownV2')

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {e}")

# --- 2. BAN USER ---
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return await update.message.reply_text("❌ Aap admin nahi hain!")
    
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Kisi user ke message par reply karke /ban likhein!")
    
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"✅ User {user_id} ko ban kar diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- 3. UNBAN USER ---
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        user_id = context.args[0]
    else:
        return await update.message.reply_text("❌ User ID dein ya message par reply karein!")

    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"✅ User {user_id} ko unban kar diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- 4. MUTE USER ---
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ User ke message par reply karein!")

    user_id = update.message.reply_to_message.from_user.id
    permissions = ChatPermissions(can_send_messages=False)
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions)
        await update.message.reply_text("🔇 User ko mute kar diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- 5. UNMUTE USER ---
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return

    user_id = update.message.reply_to_message.from_user.id
    permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, 
                                 can_send_polls=True, can_send_other_messages=True)
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions)
        await update.message.reply_text("🔊 User ko unmute kar diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- 6. PROMOTE USER ---
async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ User ke message par reply karein!")

    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id, user_id,
            can_manage_chat=True, can_delete_messages=True, 
            can_restrict_members=True, can_invite_users=True,
            can_pin_messages=True, can_manage_video_chats=True
        )
        await update.message.reply_text("🚀 User ko admin bana diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
