import asyncio
from typing import Union, Optional

from telegram import Update, Message, MessageId
from telegram.error import ChatMigrated, NetworkError, RetryAfter, TimedOut
from telegram.ext import MessageHandler, filters, ContextTypes

from forwarder import bot, REMOVE_TAG, LOGGER
from forwarder.utils import get_destination, predicate_text, get_message_type
from forwarder.utils import stats


MAX_SEND_ATTEMPTS = 5
NETWORK_BACKOFF_SECONDS = 1.0


async def send_message(
    message: Message, chat_id: int, thread_id: Optional[int] = None
) -> Union[MessageId, Message]:
    if REMOVE_TAG:
        return await message.copy(chat_id, message_thread_id=thread_id)  # type: ignore
    return await message.forward(chat_id, message_thread_id=thread_id)  # type: ignore


async def forwarder(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    source = update.effective_chat

    if not message or not source:
        return

    stats.record_received()
    dest = get_destination(source.id, message.message_thread_id)
    if not dest:
        return
    stats.COUNTERS["matched"] += 1
    message_type = get_message_type(message)

    # Captioned media usually has no message.text.
    content = message.text or message.caption or ""

    for config in dest:
        if config.message_types is not None and message_type not in config.message_types:
            stats.COUNTERS["filtered"] += 1
            continue
        # A rejected rule must not prevent later rules from being evaluated.
        if config.filters and not predicate_text(config.filters, content):
            stats.COUNTERS["filtered"] += 1
            continue
        if config.blacklist and predicate_text(config.blacklist, content):
            stats.COUNTERS["filtered"] += 1
            continue

        for chat in config.destination:
            chat_id = chat.get_id()
            thread_id = chat.get_topic()
            LOGGER.debug("Forwarding message %s to %s", source.id, chat)

            for attempt in range(1, MAX_SEND_ATTEMPTS + 1):
                try:
                    await send_message(message, chat_id, thread_id)
                    stats.record_sent()
                    break
                except RetryAfter as err:
                    if attempt == MAX_SEND_ATTEMPTS:
                        stats.COUNTERS["failed"] += 1
                        LOGGER.error(
                            "Giving up forwarding message %s from %s to %s "
                            "after %s attempts (rate limited: %s)",
                            message.message_id, source.id, chat, attempt, err,
                        )
                        break
                    wait_seconds = err.retry_after.total_seconds() if hasattr(err.retry_after, "total_seconds") else float(err.retry_after)
                    LOGGER.warning(
                        "Rate limited forwarding %s to %s (attempt %s/%s); "
                        "retrying in %.1f seconds",
                        message.message_id, chat, attempt, MAX_SEND_ATTEMPTS,
                        wait_seconds + 0.2,
                    )
                    await asyncio.sleep(wait_seconds + 0.2)
                except (TimedOut, NetworkError) as err:
                    if attempt == MAX_SEND_ATTEMPTS:
                        stats.COUNTERS["failed"] += 1
                        LOGGER.error(
                            "Giving up forwarding message %s from %s to %s "
                            "after %s attempts (network error: %s)",
                            message.message_id, source.id, chat, attempt, err,
                        )
                        break
                    wait_seconds = NETWORK_BACKOFF_SECONDS * (2 ** (attempt - 1))
                    LOGGER.warning(
                        "Network error forwarding %s to %s (attempt %s/%s): %s; "
                        "retrying in %.1f seconds",
                        message.message_id, chat, attempt, MAX_SEND_ATTEMPTS,
                        err, wait_seconds,
                    )
                    await asyncio.sleep(wait_seconds)
                except ChatMigrated as err:
                    LOGGER.warning(
                        "Chat %s migrated to %s; update chat_list.json",
                        chat_id, err.new_chat_id,
                    )
                    chat_id = err.new_chat_id
                    # Telegram group migrations do not preserve forum topic IDs.
                    thread_id = None
                    if attempt == MAX_SEND_ATTEMPTS:
                        stats.COUNTERS["failed"] += 1
                        LOGGER.error(
                            "Giving up forwarding message %s to migrated chat %s "
                            "after %s attempts",
                            message.message_id, chat_id, attempt,
                        )
                except Exception:
                    stats.COUNTERS["failed"] += 1
                    LOGGER.exception(
                        "Failed to forward message %s from %s to %s",
                        message.message_id, source.id, chat,
                    )
                    break


FORWARD_HANDLER = MessageHandler(
    filters.ALL
    & ~filters.COMMAND
    & ~filters.StatusUpdate.ALL,
    forwarder,
)
bot.add_handler(FORWARD_HANDLER)
