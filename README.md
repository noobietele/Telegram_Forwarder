# Telegram Forwarder

A Python-based Telegram bot that automatically copies or forwards messages from configured source chats to one or more destination chats.

It supports multiple forwarding routes, Telegram forum topics, message-type filtering, keyword filters, blacklist keywords, live configuration reloads, and configuration uploads through Telegram.

## Features

- Forward messages from multiple source chats.
- Send messages to multiple destination chats.
- Copy messages without the original forwarded-from attribution.
- Support Telegram groups, channels, and forum topics.
- Filter messages by type, including videos, documents, photos, audio, and text.
- Include keyword-based filters.
- Exclude messages containing blacklisted keywords.
- Handle captioned media.
- Retry temporary network errors and Telegram rate limits.
- `/status` command for forwarding statistics.
- `/reload` command to reload the configuration without restarting.
- `/upload` command to upload and activate a new `chat_list.json` through Telegram.
- `/cancel` command to cancel a pending configuration upload.

## Project Structure

```text
Telegram-Forwarder/
├── forwarder/
│   ├── modules/
│   │   ├── default.py
│   │   ├── forward.py
│   │   ├── misc.py
│   │   ├── reload.py
│   │   ├── status.py
│   │   └── upload.py
│   ├── utils/
│   │   ├── chat.py
│   │   ├── message.py
│   │   └── stats.py
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py
├── .env.example
├── .gitignore
├── chat_list.sample.json
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.9 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- Your Telegram numeric user ID
- Bot access to the source and destination chats

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Telegram-Forwarder.git
cd Telegram-Forwarder
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure environment variables

Create a file named `.env` in the project root:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
OWNER_ID=YOUR_TELEGRAM_USER_ID
REMOVE_TAG=True
```

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from BotFather |
| `OWNER_ID` | Numeric Telegram user ID of the bot owner |
| `REMOVE_TAG` | `True` copies messages without forward attribution; `False` forwards messages with attribution |

Optional configuration:

```env
CHAT_LIST_PATH=chat_list.json
```

By default, the bot reads `chat_list.json` from the project root.

**Never upload your actual `.env` file or bot token to GitHub.**

### 4. Create chat_list.json

Create a file named `chat_list.json` in the project root.

This file defines the source chats, destination chats, and forwarding rules.

Example:

```json
[
  {
    "source": -1001111111111,
    "destination": [
      -1002222222222,
      -1003333333333
    ]
  }
]
```

Replace the example IDs with your actual Telegram chat IDs.

## Configuration Guide

Each forwarding rule supports the following fields:

| Field | Required | Description |
|---|---|---|
| `source` | Yes | Source chat ID, optionally followed by a topic ID |
| `destination` | Yes | List of destination chat IDs, optionally with topic IDs |
| `message_types` | No | Allowed message types |
| `filters` | No | Messages must contain at least one matching keyword |
| `blacklist` | No | Messages containing any matching keyword are rejected |

### Multiple destinations

One source can forward messages to multiple destinations:

```json
[
  {
    "source": -1001111111111,
    "destination": [
      -1002222222222,
      -1003333333333
    ]
  }
]
```

### Message-type filtering

Forward only videos and documents:

```json
[
  {
    "source": -1001111111111,
    "destination": [-1002222222222],
    "message_types": ["video", "document"]
  }
]
```

Supported message types:

- `text`
- `photo`
- `video`
- `document`
- `audio`
- `voice`
- `animation`
- `sticker`
- `video_note`
- `contact`
- `location`
- `poll`
- `other`

If `message_types` is omitted, all supported message types are allowed.

### Keyword filtering

Forward messages containing 1080p or 2160p, while excluding CAMRip and HDCAM:

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

Filter behaviour:

- Multiple `filters` entries use OR matching: at least one must match.
- Multiple `blacklist` entries use OR matching: any match rejects the message.
- Matching is case-insensitive.
- Matching uses whole-word boundaries.
- Message captions are checked along with text.

### Forum topic forwarding

You can route a specific source forum topic to a specific destination forum topic.

Format:

```text
CHAT_ID#TOPIC_ID
```

Example:

```json
[
  {
    "source": "-1001111111111#100",
    "destination": [
      "-1002222222222#200"
    ],
    "message_types": ["video", "document"]
  }
]
```

This forwards messages from topic `100` in the source group to topic `200` in the destination group.

### Complete configuration example

```json
[
  {
    "source": -1001111111111,
    "destination": [
      -1002222222222,
      -1003333333333
    ]
  },
  {
    "source": -1004444444444,
    "destination": [-1005555555555],
    "message_types": ["video", "document"]
  },
  {
    "source": "-1006666666666#100",
    "destination": ["-1007777777777#200"],
    "message_types": ["video", "document"]
  },
  {
    "source": -1008888888888,
    "destination": [-1009999999999],
    "message_types": ["video", "document"],
    "filters": ["1080p", "2160p"],
    "blacklist": ["CAMRip", "HDCAM"]
  }
]
```

## Telegram Bot Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/help` | Display available commands |
| `/id` | Get your chat ID and forum topic ID |
| `/status` | Display forwarding statistics |
| `/reload` | Reload `chat_list.json` from disk |
| `/upload` | Upload a new `chat_list.json` |
| `/cancel` | Cancel a pending configuration upload |

The owner-only commands are restricted to the configured owner in private chat.

### Updating configuration

You have two options:

**Option 1: Edit on the server**

Edit `chat_list.json`, then send:

```text
/reload
```

**Option 2: Upload through Telegram**

1. Send `/upload` to the bot privately.
2. Upload a document named exactly `chat_list.json`.
3. The bot validates the configuration.
4. If valid, the new configuration is activated without restarting.

The upload limit is 1 MB. Invalid configurations are rejected without replacing the active routes.

## Running the Bot

Start the bot using:

```bash
python3 -m forwarder
```

The bot uses Telegram polling to receive messages.

To stop it, press:

```text
Ctrl + C
```

## Running on Oracle Cloud / Ubuntu

The bot can run directly on an Ubuntu VPS.

### Install screen

```bash
sudo apt update
sudo apt install screen -y
```

### Start a persistent session

```bash
screen -S tgforwarder
```

Enter your project directory:

```bash
cd ~/Telegram-Forwarder
```

Start the bot:

```bash
python3 -m forwarder
```

Detach from the screen session:

- Press `Ctrl + A`
- Then press `D`

The bot continues running after you disconnect from SSH.

### Screen commands

List sessions:

```bash
screen -ls
```

Reconnect:

```bash
screen -r tgforwarder
```

Stop the bot:

Reconnect to the session and press `Ctrl + C`.

## Permissions and Setup

Before using the bot:

1. Add the bot to your source groups and channels.
2. Ensure it has permission to access source messages.
3. Give it permission to send messages in destination groups.
4. For channels, provide the necessary administrator permissions.
5. For forum destinations, ensure it can post in the required topics.
6. Use `/id` to identify chat and topic IDs.

Telegram bot privacy settings and channel permissions may affect which messages the bot can receive.

## Troubleshooting

**Bot does not start**

- Verify `BOT_TOKEN` in `.env`.
- Check that `chat_list.json` exists.
- Verify JSON syntax.
- Install dependencies again if necessary.

**Messages are not forwarding**

- Verify source and destination IDs.
- Check bot membership and permissions.
- Check whether the message matches the configured filters.
- For topic routes, verify both topic IDs.

**Configuration changes are not applied**

- Check the JSON syntax.
- Send `/reload` after editing the file.
- Check the bot logs for validation errors.

**Bot encounters rate limits**

The forwarder retries Telegram rate-limit responses and temporary network errors up to a bounded number of attempts. Messages that exhaust retries are logged as failures.

## Security

- Never commit `.env`.
- Never publish your bot token.
- Do not commit personal session files or private configuration.
- Use a private repository if your source code or configuration should not be public.
- Keep a backup of your working configuration.

## Technology

- Python
- python-telegram-bot
- python-dotenv
- Telegram Bot API

## Disclaimer

This project is intended for legitimate Telegram message forwarding and chat management. Use it only in chats where you have appropriate access and permission to forward or copy content.

---

**Configuration files:** Use `.env.example` and `chat_list.sample.json` as templates. Create your own `.env` and `chat_list.json` locally before running the bot.
