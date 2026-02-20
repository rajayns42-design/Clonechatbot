from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

# =========================
# HELPER: Admin Check
# =========================
async def is_admin(update: Update) -> bool:
    """Check karta hai ki command chalane wala admin hai ya nahi"""
    try:
        user_status = (await update.effective_chat.get_member(update.effective_user.id)).status
        return user_status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except:
        return False

# =========================
# ADMIN LIST
# =========================
async def get_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        return await update.message.reply_text("❌ Ye command sirf groups mein kaam karti hai!")

    status_msg = await update.message.reply_text("🔍 **Admins ki list nikaal raha hoon...**")

    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        owner_text = ""
        admins_text = ""
        for admin in admins:
            user = admin.user
            mention = user.mention_markdown_v2()
            if admin.status == ChatMemberStatus.OWNER:
                owner_text = f"👑 **Owner:**\n└ {mention}\n\n"
            else:
                admins_text += f"├ {mention}\n"

        admins_text = "✨ **Admins:**\n" + admins_text[:-1].replace("├", "└", 1) if admins_text else "└ No other admins found."
        full_message = f"👮 **Admin List for {chat.title}:**\n\n{owner_text}{admins_text}"

        await status_msg.edit_text(full_message, parse_mode='MarkdownV2')
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {e}")

# =========================
# BAN / UNBAN / MUTE / UNMUTE / PROMOTE
# =========================
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

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    user_id = update.message.reply_to_message.from_user.id if update.message.reply_to_message else None
    if not user_id: return await update.message.reply_text("❌ User ka ID provide karein ya reply karein!")
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"✅ User {user_id} ko unban kar diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply karein jise mute karna hai!")
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text("🔇 User ko mute kar diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                      can_send_polls=True, can_send_other_messages=True)
        await context.bot.restrict_chat_member(update.effective_chat.id, user_id, permissions)
        await update.message.reply_text("🔊 User ko unmute kar diya gaya!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply karein jise promote karna hai!")
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

# =========================
# USER INFO / ID COMMAND (Professional)
# =========================
async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/id command - Admin safe + professional"""
    requester = update.effective_user
    chat = update.effective_chat

    # Admin check
    try:
        member_status = (await chat.get_member(requester.id)).status
        is_admin_flag = member_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        is_admin_flag = False

    # Target user: reply user for admins, self for non-admin
    if update.message.reply_to_message and is_admin_flag:
        user = update.message.reply_to_message.from_user
    else:
        user = requester

    first_name = user.first_name or "N/A"
    last_name = user.last_name or ""
    username = f"@{user.username}" if user.username else "N/A"
    user_id = user.id
    mention = f"[{first_name}](tg://user?id={user_id})"

    text = (
        f"👤 **User Info**\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"📝 Name: {first_name} {last_name}\n"
        f"🔗 Username: {username}\n"
        f"💬 Mention: {mention}\n"
        f"⚠️ Accessed by: {requester.first_name}"
    )

    # Profile photo button
    buttons = [[InlineKeyboardButton("📷 View Profile Photo", url=f"https://t.me/i/user/{user_id}")]] \
        if user else []

    await update.message.reply_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
            )
