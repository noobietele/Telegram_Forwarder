# Telegram Forwarder

A Python-based Telegram bot for routing messages from configured source chats to one or more destination chats.

## Features

- Multiple source-to-destination routes
- Multiple destinations per source
- Message-type filters
- Keyword inclusion and blacklist filters
- Caption-aware filtering
- Forum topic routing
- Runtime configuration reload with `/reload`
- Configuration upload through Telegram with `/upload`
- Forwarding statistics with `/status`

## Project structure

```text
Telegram-Forwarder/
├── forwarder/
│   ├── modules/
│   └── utils/
├── .env.example
├── .gitignore
├── chat_list.sample.json
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.9 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- Your numeric Telegram user ID
- Appropriate bot access and permissions in source and destination chats

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/Telegram-Forwarder.git
cd Telegram-Forwarder
pip3 install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
nano .env
```

Create your runtime configuration from the sample:

```bash
cp chat_list.sample.json chat_list.json
nano chat_list.json
```

Replace all example chat and topic IDs with your own.

## Environment variables

```env
BOT_TOKEN=YOUR_BOT_TOKEN
OWNER_ID=YOUR_TELEGRAM_USER_ID
REMOVE_TAG=True
# CHAT_LIST_PATH=chat_list.json
```

- `BOT_TOKEN`: token obtained from BotFather.
- `OWNER_ID`: numeric Telegram user ID of the owner.
- `REMOVE_TAG`: controls whether messages are copied without the forwarded-from attribution.
- `CHAT_LIST_PATH`: optional path to the routing configuration; by default the project uses `chat_list.json`.

Never commit your real `.env` file or private `chat_list.json`.

## Routing configuration

`chat_list.json` contains a JSON array of route objects.

### One source to multiple destinations

```json
[
  {
    "source": -1001111111111,
    "destination": [-1002222222222, -1003333333333]
  }
]
```

### Filter by message type

```json
[
  {
    "source": -1001111111111,
    "destination": [-1002222222222],
    "message_types": ["video", "document"]
  }
]
```

### Keyword filters and blacklist

```json
[
  {
    "source": -1001111111111,
    "destination": [-1002222222222],
    "message_types": ["video", "document"],
    "filters": ["1080p", "2160p"],
    "blacklist": ["CAMRip", "HDCAM"]
  }
]
```

The intended filter logic is: at least one `filters` keyword must match when that field is present; a match against any `blacklist` keyword rejects the message. Text and media captions may be checked.

### Forum topic routing

The topic notation used by this project is:

```text
CHAT_ID#TOPIC_ID
```

Example:

```json
[
  {
    "source": "-1001111111111#100",
    "destination": ["-1002222222222#200"]
  }
]
```

Use the actual chat IDs and topic IDs from your Telegram groups.

## Commands

- `/start` — start interacting with the bot
- `/help` — show available commands
- `/id` — display chat/topic identifiers
- `/status` — display forwarding statistics
- `/reload` — reload the routing configuration from disk
- `/upload` — upload a replacement `chat_list.json`
- `/cancel` — cancel a pending configuration upload

Availability and access to commands depend on the implementation and owner checks in the project.

## Run

Start the bot from the project root:

```bash
python3 -m forwarder
```

Stop it with `Ctrl+C`.

## Run persistently on Ubuntu / Oracle Cloud with screen

```bash
sudo apt update
sudo apt install screen -y
screen -S tgforwarder
cd ~/Telegram-Forwarder
python3 -m forwarder
```

Detach with `Ctrl+A`, then `D`.

Useful commands:

```bash
screen -ls
screen -r tgforwarder
```

To stop the bot, reattach and press `Ctrl+C`.

## Permissions

Add the bot to the required source and destination chats. Give it the permissions required to receive source updates and send messages to destinations. For channels and forum topics, verify the relevant administrator and posting permissions.

## Security

- Keep `.env` private.
- Do not commit real chat IDs or private routing configuration if they are sensitive.
- Do not commit Telegram session files, tokens, logs, or virtual environments.
- Use `.env.example` and `chat_list.sample.json` as safe templates.

## Disclaimer

Use this software only in chats where you have permission to access and copy or forward messages. Respect Telegram's terms and the rights of content owners.
