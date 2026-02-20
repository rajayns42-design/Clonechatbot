from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

# =========================
# HELPER: Admin Check
# =========================
async def is_admin(update: Update) -> bool:
    try:
        user_status = (await update.effective_chat.get_member(update.effective_user.id)).status
        return user_status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except:
        return False

# =========================
# PROMOTE / DEMOTE Logic
# =========================
async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return await update.message.reply_text("<blockquote>❌ Aap admin nahi hain!</blockquote>", parse_mode="HTML")
    if not update.message.reply_to_message:
        return await update.message.reply_text("<blockquote>❌ Reply to a user to promote!</blockquote>", parse_mode="HTML")
    
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id, user.id,
            can_manage_chat=True, can_post_messages=True, can_edit_messages=True,
            can_delete_messages=True, can_invite_users=True, can_restrict_members=True,
            can_pin_messages=True, can_promote_members=False
        )
        await update.message.reply_text(f"<blockquote>✅ <b>Promoted:</b> {user.first_name}</blockquote>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("<blockquote>❌ Reply to a user to demote!</blockquote>", parse_mode="HTML")
    
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.promote_chat_member(
            update.effective_chat.id, user.id,
            can_manage_chat=False, can_post_messages=False, can_edit_messages=False,
            can_delete_messages=False, can_invite_users=False, can_restrict_members=False,
            can_pin_messages=False, can_promote_members=False
        )
        await update.message.reply_text(f"<blockquote>📉 <b>Demoted:</b> {user.first_name}</blockquote>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# =========================
# BAN / UNBAN / MUTE / UNMUTE
# =========================
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"<blockquote>✅ <b>Banned:</b> {user.first_name}</blockquote>", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"<blockquote>🔓 <b>Unbanned:</b> {user.first_name}</blockquote>", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text(f"<blockquote>🔇 <b>Muted:</b> {user.first_name}</blockquote>", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if not update.message.reply_to_message: return
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
        await update.message.reply_text(f"<blockquote>🔊 <b>Unmuted:</b> {user.first_name}</blockquote>", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")

# =========================
# ADMIN LIST & USER INFO
# =========================
async def get_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return
    status_msg = await update.message.reply_text("🔍 <b>Admins ki list nikaal raha hoon...</b>", parse_mode="HTML")
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        owner_text = ""
        admins_text = ""
        for admin in admins:
            user = admin.user
            mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            if admin.status == ChatMemberStatus.OWNER:
                owner_text = f"👑 <b>Owner:</b>\n└ {mention}\n\n"
            else:
                admins_text += f"├ {mention}\n"
        if admins_text:
            admins_text = "✨ <b>Admins:</b>\n" + admins_text[:-1].replace("├", "└", 1)
        await status_msg.edit_text(f"👮 <b>Admin List: {chat.title}</b>\n<blockquote>\n{owner_text}{admins_text}\n</blockquote>", parse_mode='HTML')
    except Exception as e: await status_msg.edit_text(f"❌ Error: {e}")

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    text = f"👤 <b>User Info</b>\n<blockquote>\n🆔 <b>ID:</b> <code>{user.id}</code>\n📝 <b>Name:</b> {user.first_name}\n🏷 <b>User:</b> @{user.username if user.username else 'N/A'}\n</blockquote>"
    await update.message.reply_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📷 Profile", url=f"https://t.me/i/user/{user.id}")]]))
