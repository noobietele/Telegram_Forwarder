"""Upload and activate chat_list.json by sending it to the bot privately."""
import asyncio
import json
import os
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters

from forwarder import OWNER_ID, bot, LOGGER
from forwarder.utils.chat import parse_config, reload_config

CONFIG_PATH = Path(os.getenv("CHAT_LIST_PATH", "chat_list.json"))
MAX_CONFIG_BYTES = 1024 * 1024  # Prevent unexpectedly large downloads.
UPLOAD_LOCK = asyncio.Lock()
# Pending /upload is in memory; restart clears it.
PENDING_USERS = set()


def _validate(content: bytes) -> int:
    try:
        raw = json.loads(content.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise ValueError(f"File must contain valid UTF-8 JSON: {exc}") from exc
    return len(parse_config(raw))


async def request_upload(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.effective_message
    if user is None or message is None:
        return
    PENDING_USERS.add(user.id)
    await message.reply_text(
        "Send chat_list.json as a Telegram document in this private chat.\n"
        "The bot will validate every route before replacing the current configuration.\n"
        "Send /cancel to cancel. Maximum file size: 1 MB."
    )


async def cancel_upload(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None or update.effective_message is None:
        return
    PENDING_USERS.discard(user.id)
    await update.effective_message.reply_text("Upload cancelled.")


async def receive_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None or message.document is None:
        return
    if user.id not in PENDING_USERS:
        return
    document = message.document
    if document.file_name != "chat_list.json":
        await message.reply_text("Please upload a document named exactly chat_list.json, or send /cancel.")
        return
    if document.file_size is None or document.file_size > MAX_CONFIG_BYTES:
        await message.reply_text("File is too large or has unknown size (maximum 1 MB).")
        return
    # Serialize uploads with /reload, so a valid upload won't race a disk reload.
    async with UPLOAD_LOCK:
        temp_path = None
        try:
            telegram_file = await context.bot.get_file(document.file_id)
            content = bytes(await telegram_file.download_as_bytearray())
            if len(content) > MAX_CONFIG_BYTES:
                raise ValueError("Downloaded file exceeds 1 MB")
            count = _validate(content)
            # Write in the same directory so os.replace is atomic on the filesystem.
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".chat_list.", suffix=".tmp",
                dir=str(CONFIG_PATH.resolve().parent), delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            # Validation is complete before changing the original file.
            os.replace(temp_path, CONFIG_PATH)
            temp_path = None
            reload_config(str(CONFIG_PATH))
        except Exception as exc:
            LOGGER.exception("Configuration upload failed")
            await message.reply_text(f"Upload rejected. Active routes were not changed.\n{exc}")
            return
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
    PENDING_USERS.discard(user.id)
    await message.reply_text(f"✅ Uploaded and activated chat_list.json: {count} routes active. No restart needed.")


OWNER_PRIVATE = filters.User(OWNER_ID) & filters.ChatType.PRIVATE
bot.add_handler(CommandHandler("upload", request_upload, filters=OWNER_PRIVATE))
bot.add_handler(CommandHandler("cancel", cancel_upload, filters=OWNER_PRIVATE))
bot.add_handler(MessageHandler(OWNER_PRIVATE & filters.Document.ALL, receive_upload), group=-1)
