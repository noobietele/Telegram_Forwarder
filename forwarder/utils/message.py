import re

from typing import List


def predicate_text(filters: List[str], text: str) -> bool:
    """Check if the text contains any of the filters"""
    for i in filters:
        pattern = r"( |^|[^\w])" + re.escape(i) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def get_message_type(message) -> str:
    """Classify a Telegram message using its principal content type."""
    for name in (
        "text", "photo", "video", "document", "audio", "voice",
        "animation", "sticker", "video_note", "contact", "location", "poll",
    ):
        if getattr(message, name, None):
            return name
    return "other"
