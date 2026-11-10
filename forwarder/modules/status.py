"""Owner-only /status showing the bot's current in-memory state."""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters

from forwarder import OWNER_ID, bot
from forwarder.utils.chat import get_config
from forwarder.utils import stats


async def status(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if msg is None:
        return
    routes = get_config()
    sources = {route.source.get_id() for route in routes}
    destinations = {dest.get_id() for route in routes for dest in route.destination}
    counts = stats.COUNTERS
    await msg.reply_text(
        "🟢 Telegram Forwarder is running\n"
        f"Uptime: {stats.uptime()}\n"
        f"Active routes: {len(routes)}\n"
        f"Source chats: {len(sources)}\n"
        f"Destination chats: {len(destinations)}\n"
        f"Incoming messages: {counts['received']}\n"
        f"Messages with matching source/topic: {counts['matched']}\n"
        f"Route rules filtered out: {counts['filtered']}\n"
        f"Successful destination deliveries: {counts['sent']}\n"
        f"Failed destination deliveries: {counts['failed']}\n"
        f"Last incoming message: {stats.fmt_time(stats.LAST_MESSAGE_AT)}\n"
        f"Last successful delivery: {stats.fmt_time(stats.LAST_SENT_AT)}\n\n"
        "Counters reset when the bot restarts. "
        "Running means the process is responding, not that each route has been verified."
    )


bot.add_handler(CommandHandler(
    "status", status,
    filters=filters.User(OWNER_ID) & filters.ChatType.PRIVATE,
))
