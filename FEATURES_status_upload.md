# Added features: /status and /upload

Works with existing `chat_list.json`, message-type filtering, `/reload`, and the three forwarding fixes.

## /status

From a private chat with the bot, send `/status` using the Telegram account whose numeric ID is `OWNER_ID` in `.env`.

It reports process uptime, active routes, distinct source/destination chats, received messages, matched messages, filtered route rules, successful destination deliveries, failed destination deliveries, and last-activity times. Counts are held in memory and reset when the bot restarts. A success counts a completed Bot API call; it does not guarantee a human has read the message.

## /upload

1. Send `/upload` to the bot from `OWNER_ID` in **private chat**.
2. Send the replacement **chat_list.json** file as a Telegram **document** (not pasted as text). Maximum 1 MiB.
3. The bot downloads it, decodes UTF-8 JSON, validates all routing entries, saves it to `chat_list.json` using a same-directory atomic replacement, and immediately reloads it. A reply confirms the number of active routes.
4. For invalid JSON or routes, the active configuration remains untouched and the upload can be retried.
5. Send `/cancel` to cancel a pending upload.

The filename must be exactly `chat_list.json`. The upload replaces the full configuration, not just one route. Make a local backup of the old configuration before the first upload. `/reload` is also serialized with uploads.

The bot process must have **write access to the directory containing `chat_list.json`**; it is not enough for the file alone to be writable because atomic replacement creates a temporary file and renames it. The updated Docker Compose now mounts `./config:/app/config` and sets `CHAT_LIST_PATH=/app/config/chat_list.json` to allow atomic replacement. **Before your first Docker Compose startup, create `config/` and copy your existing `chat_list.json` into `config/chat_list.json`.** Running via Python directly keeps the default `chat_list.json` in your working directory. A legacy single-file Docker bind mount can cause atomic replacement to fail with `Device or resource busy`.

The command cannot modify `.env`, bot permissions, or Telegram API delivery limits. On ephemeral hosting without persistent storage, uploads disappear on redeploy or restart if the platform discards the filesystem. Always use persistent storage for `chat_list.json`.

**Important:** The owner ID restriction is enforced on commands and uploaded documents, and private chat is mandatory. Do not give other accounts access to `OWNER_ID`.
