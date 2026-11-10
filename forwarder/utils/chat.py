import json
from os import getenv
from pathlib import Path
from typing import List, Optional, Union

from forwarder import CONFIG

# Values supported in chat_list.json. Omit message_types to allow everything.
MESSAGE_TYPES = frozenset({
    "text", "photo", "video", "document", "audio", "voice",
    "animation", "sticker", "video_note", "contact", "location",
    "poll", "other",
})

PARSED_CONFIG = None


class ChatConfig:
    def __init__(self, chat_id: Union[str, int]):
        self.__chat = chat_id

    def __repr__(self):
        if self.is_topic:
            return f"{self.get_id()}#{self.get_topic()}"
        return str(self.get_id())

    @property
    def is_topic(self):
        return isinstance(self.__chat, str) and len(self.__chat.split("#")) == 2

    def get_topic(self) -> Optional[int]:
        if not self.is_topic:
            return None
        return int(self.__chat.split("#")[1])

    def get_id(self) -> int:
        if isinstance(self.__chat, int):
            return self.__chat
        return int(self.__chat.split("#")[0])


class ForwardConfig:
    def __init__(
        self, source: Union[str, int], destination: List[Union[str, int]],
        filters: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None,
        message_types: Optional[List[str]] = None,
    ):
        self.source = ChatConfig(source)
        self.destination = [ChatConfig(item) for item in destination]
        self.filters = filters
        self.blacklist = blacklist
        self.message_types = set(message_types) if message_types is not None else None


def parse_config(raw) -> List[ForwardConfig]:
    """Validate the complete file before swapping any live routes."""
    if not isinstance(raw, list):
        raise ValueError("chat_list.json must contain a JSON array of routes")

    parsed = []
    for index, route in enumerate(raw, 1):
        if not isinstance(route, dict):
            raise ValueError(f"Route {index}: expected an object")
        if "source" not in route or "destination" not in route:
            raise ValueError(f"Route {index}: source and destination are required")
        destination = route["destination"]
        if not isinstance(destination, list) or not destination:
            raise ValueError(f"Route {index}: destination must be a nonempty list")
        for key in ("filters", "blacklist", "message_types"):
            value = route.get(key)
            if value is not None and (not isinstance(value, list) or not all(isinstance(x, str) for x in value)):
                raise ValueError(f"Route {index}: {key} must be a list of strings")
        types = route.get("message_types")
        if types is not None:
            unknown = set(types) - MESSAGE_TYPES
            if unknown:
                raise ValueError(f"Route {index}: unsupported message_types: {sorted(unknown)}")
        try:
            config = ForwardConfig(
                route["source"], destination,
                route.get("filters"), route.get("blacklist"), types,
            )
            config.source.get_id()
            config.source.get_topic()
            for chat in config.destination:
                chat.get_id()
                chat.get_topic()
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError(f"Route {index}: invalid chat/topic ID: {exc}") from exc
        parsed.append(config)
    return parsed


def get_config() -> List[ForwardConfig]:
    global PARSED_CONFIG
    if PARSED_CONFIG is None:
        PARSED_CONFIG = parse_config(CONFIG)
    return PARSED_CONFIG


def reload_config(filename=None) -> int:
    """Read, validate, then atomically swap in the new route list.

    On JSON or validation failure the current active routes stay unchanged.
    """
    global PARSED_CONFIG
    if filename is None:
        filename = getenv("CHAT_LIST_PATH", "chat_list.json")
    with Path(filename).open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    new_routes = parse_config(raw)
    PARSED_CONFIG = new_routes
    return len(new_routes)


def get_destination(chat_id: int, topic_id: Optional[int] = None) -> List[ForwardConfig]:
    return [
        chat for chat in get_config()
        if chat.source.get_id() == chat_id and chat.source.get_topic() == topic_id
    ]
