# Added features: message type filtering and /reload

## Message type filtering

Add an optional `message_types` list to any route in `chat_list.json`.
A route without this field still forwards all message types as before.
An empty list (`[]`) forwards nothing for that route.

Examples:

```json
[
  {"source": -1001111111111, "destination": [-1002222222222], "message_types": ["video", "document"]},
  {"source": -1003333333333, "destination": [-1004444444444], "message_types": ["text", "photo"], "filters": ["movie"]}
]
```

Valid types: `text`, `photo`, `video`, `document`, `audio`, `voice`,
`animation`, `sticker`, `video_note`, `contact`, `location`, `poll`, `other`.

`document` matches Telegram documents (including `.torrent` and uploaded files).
For files sent as video messages, use `video`.
For media captions, existing `filters` and `blacklist` continue to work.

## /reload

1. Edit and save `chat_list.json` on the server.
2. In a private Telegram chat with the bot, send `/reload` from `OWNER_ID`.
3. The bot checks and loads the complete file. If any route is invalid,
   the old configuration remains active.
4. Add and remove source chats without restarting. The forwarding handler
   now examines incoming messages and routes only configured sources.

Important: editing `.env`, `BOT_TOKEN`, `OWNER_ID`, or `REMOVE_TAG` still
requires restarting the process. The bot must already be a member of newly
configured source chats and have permission to receive their messages.

No historical message backlog is fetched by /reload; only subsequent updates
are processed against the new rules.
