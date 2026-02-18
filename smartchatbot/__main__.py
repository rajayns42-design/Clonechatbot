import logging
import asyncio

from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from .config import TOKEN
from .database import get_all_bots

from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member
from .modules.cloner import (
    clone_bot,
    clone_start_handler,
    anti_nsfw_delete,
    broadcast_handler,
    delclone_bot
)

from .modules.admin import (
    ban_user,
    unban_user,
    mute_user,
    unmute_user,
    promote_user,
    get_admin_list
)

from .modules.ping import ping_handler, ping_callback_handler


# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# =========================
# UI COMMAND MENU
# =========================

async def set_ui_commands(bot):

    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("ping", "Check speed"),
        BotCommand("clone", "Create clone"),
        BotCommand("delclone", "Delete clone"),
        BotCommand("chatbot", "Toggle chatbot"),
        BotCommand("welcome", "Toggle welcome"),
        BotCommand("adminlist", "Admins list"),
        BotCommand("broadcast", "Owner only broadcast"),
    ]

    await bot.set_my_commands(commands)


# =========================
# REGISTER HANDLERS
# =========================

def register_all_handlers(app: Application):

    # start
    app.add_handler(CommandHandler("start", clone_start_handler))

    # clone system
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))

    # broadcast (owner check inside module)
    app.add_handler(CommandHandler("broadcast", broadcast_handler))

    # ping
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(
        CallbackQueryHandler(
            ping_callback_handler,
            pattern="close_ping"
        )
    )

    # admin tools
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # feature toggles
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    # chatbot replies (unlimited lifetime)
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chatbot_reply
        )
    )

    # welcome new members
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_member
        )
    )

    # anti media delete
    app.add_handler(
        MessageHandler(
            (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL)
            & ~filters.COMMAND,
            anti_nsfw_delete
        ),
        group=1
    )


# =========================
# RESTART CLONES FROM DB
# =========================

async def restart_clones(main_app: Application):

    bots = get_all_bots()

    if not bots:
        logging.info("No clones to restart")
        return

    for bot in bots:
        try:
            clone_app = (
                Application.builder()
                .token(bot["token"])
                .job_queue(True)
                .build()
            )

            await set_ui_commands(clone_app.bot)
            register_all_handlers(clone_app)

            await clone_app.initialize()
            await clone_app.start()

            logging.info(f"✅ Clone started @{bot.get('username')}")

        except Exception as e:
            logging.error(f"❌ Clone failed: {e}")


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:
        print("TOKEN missing")
        return

    app = (
        Application.builder()
        .token(TOKEN)
        .job_queue(True)
        .build()
    )

    # set command menu after boot
    app.job_queue.run_once(
        lambda c: asyncio.create_task(set_ui_commands(app.bot)),
        1
    )

    # restart clones after boot
    app.job_queue.run_once(
        lambda c: asyncio.create_task(restart_clones(app)),
        5
    )

    register_all_handlers(app)

    print("⚡ MAIN BOT RUNNING ⚡")
    app.run_polling()


# =========================

if __name__ == "__main__":
    main()
