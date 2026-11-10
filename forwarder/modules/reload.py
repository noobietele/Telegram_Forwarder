from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters

from forwarder import OWNER_ID, bot, LOGGER
from forwarder.utils.chat import reload_config
from forwarder.modules.upload import UPLOAD_LOCK


async def reload_routes(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    try:
        async with UPLOAD_LOCK:
            count = reload_config()
    except (OSError, ValueError) as exc:
        LOGGER.warning("Configuration reload rejected: %s", exc)
        await message.reply_text(f"Reload failed; previous routes remain active.\n{exc}")
        return
    await message.reply_text(f"Configuration reloaded successfully: {count} routes active.")


# Owner-only and private-only, so group members cannot trigger a reload.
bot.add_handler(CommandHandler(
    "reload", reload_routes,
    filters=filters.User(OWNER_ID) & filters.ChatType.PRIVATE,
))
