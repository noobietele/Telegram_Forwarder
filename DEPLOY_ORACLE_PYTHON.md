# Oracle Cloud deployment (direct Python)

1. Stop the currently running bot process before replacing code.
2. Back up the whole existing project directory, especially `.env` and `chat_list.json`.
3. Extract this archive and copy the complete `Telegram_Forwarder-master` project contents into the deployment directory. Do not overwrite `.env` or `chat_list.json` with sample files.
4. Keep using the existing Python virtual environment if one is already used. Install dependencies only if needed: `python3 -m pip install -r requirements.txt`.
5. Ensure `.env` contains the existing `BOT_TOKEN`, your numeric personal `OWNER_ID`, and `REMOVE_TAG` setting.
6. Ensure `chat_list.json` is in the working directory, or set `CHAT_LIST_PATH` in `.env` to its absolute path.
7. Validate syntax: `python3 -m compileall -q forwarder`.
8. Start: `python3 -m forwarder`.
9. Test `/status`, `/reload`, then `/upload` in a private chat with the owner account. First upload an unchanged copy of the current config.

Run one bot process per bot token. For persistence after SSH disconnect, run it inside `screen` or manage it with systemd. Oracle's local disk persists across normal process and VM restarts, but keep backups.

## Configuration upload behavior

`/upload` accepts a Telegram document named exactly `chat_list.json` from the configured owner in private chat. The file is limited to 1 MiB, parsed and validated before replacement, and written using an atomic same-filesystem rename. `/cancel` clears the pending upload. `/reload` reloads the file already on disk. Both operations share a lock.

Counters shown by `/status` are in-memory and reset when the process restarts. The bot cannot recover Telegram updates it never received.
