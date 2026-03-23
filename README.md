<div align="center">

# 🤖 Termux Telegram AI Agent

**A private AI assistant that lives on your Android phone.**
Run it inside Termux, control it through Telegram, powered by OpenAI.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram)](https://core.telegram.org/bots)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai)](https://openai.com)
[![Termux](https://img.shields.io/badge/Platform-Termux%20%2F%20Android-green?style=flat-square)](https://termux.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## 📖 What Is This?

**Termux Telegram AI Agent** is a lightweight Python bot that runs continuously on your Android phone inside [Termux](https://termux.dev). It connects to your personal Telegram bot and uses the OpenAI API to respond intelligently to your messages — like having a pocket AI assistant available 24/7.

No cloud server. No monthly hosting fees. Just your phone.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔒 Private & Secure | Only your Telegram user ID can interact with it |
| 🧠 Smart AI Replies | Powered by OpenAI (`gpt-4o-mini` by default) |
| 💬 Conversation Memory | Remembers context within a session |
| 🤔 Thinking Indicator | Shows "Thinking..." while the AI processes |
| 📱 Termux Native | Runs on Android with no root required |
| 🔁 Auto-Retry | Retries failed API calls automatically |
| 📋 Command System | `/help`, `/status`, `/clear`, `/about` |
| 📝 Clean Logging | Logs to terminal and `agent.log` file |
| ✂️ Long Message Splitting | Auto-splits responses over 4000 chars |
| ⚙️ Easy Config | Single `config.json` file for all settings |

---

## 📁 Project Structure

```
Termux-Telegram-AI-Agent/
│
├── main.py          ← Main bot script (all logic lives here)
├── config.json      ← Your API keys and settings (fill this in)
├── requirements.txt ← Python dependencies
├── README.md        ← This file
└── agent.log        ← Auto-created log file when the bot runs
```

---

## 🚀 Setup Guide (Termux — Step by Step)

Follow these steps exactly. Each command is ready to copy and paste.

---

### Step 1 — Install Termux

Download **Termux from F-Droid** (NOT the Play Store version — it's outdated):

👉 https://f-droid.org/packages/com.termux/

---

### Step 2 — Update Termux Packages

Open Termux and run:

```bash
pkg update && pkg upgrade -y
```

> This may take a few minutes on first run. Type `y` and press Enter if prompted.

---

### Step 3 — Install Python and Git

```bash
pkg install python git -y
```

Verify the installation:

```bash
python --version
git --version
```

You should see version numbers for both.

---

### Step 4 — Clone This Repository

```bash
git clone https://github.com/Marcusbennettnyx/Termux-Telegram-AI-Agent.git
---

### Step 5 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `python-telegram-bot` — Telegram bot framework
- `openai` — OpenAI Python client
- `httpx` — HTTP client (dependency)

---

### Step 6 — Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send the command: `/newbot`
3. Choose a name for your bot (e.g., `My AI Agent`)
4. Choose a username ending in `bot` (e.g., `myai_phone_bot`)
5. BotFather will give you a **Bot Token** — it looks like:
   ```
   1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
6. Copy and save this token — you'll need it in the next step.

---

### Step 7 — Get Your Telegram User ID

1. Open Telegram and search for **@userinfobot**
2. Send it any message (e.g., `/start`)
3. It will reply with your **User ID** — a number like `987654321`
4. Copy and save this number.

> Your User ID is how the bot knows that *you* are authorized to use it.

---

### Step 8 — Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click **Create new secret key**
3. Copy the key — it starts with `sk-...`

> ⚠️ OpenAI API requires a paid account. `gpt-4o-mini` is very cheap (~$0.0002 per 1K tokens).

---

### Step 9 — Configure the Bot

Open `config.json` in Termux using nano:

```bash
nano config.json
```

Fill in your values:

```json
{
  "TELEGRAM_BOT_TOKEN": "1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "OPENAI_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "AUTHORIZED_USER_ID": "987654321",

  "AI_MODEL": "gpt-4o-mini",

  "SYSTEM_PROMPT": "You are a helpful, concise, and smart AI assistant running on an Android phone via Termux. Keep responses clear and well-structured.",

  "MAX_RETRIES": 3
}
```

Save and exit nano:
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter`

---

### Step 10 — Run the Bot

```bash
python main.py
```

You should see:

```
═══════════════════════════════════════════════════════
  🤖  Termux Telegram AI Agent
═══════════════════════════════════════════════════════
  Model       : gpt-4o-mini
  Auth User   : 987654321
  Max Retries : 3
  Started at  : 2025-01-01 12:00:00
═══════════════════════════════════════════════════════
  Polling for messages... (Ctrl+C to stop)
```

Now open Telegram, go to your bot, and send it a message!

---

## 💬 Bot Commands

Once the bot is running, these commands are available:

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` | Usage guide |
| `/status` | Show bot status and model info |
| `/clear` | Clear conversation memory |
| `/about` | About this project |

---

## ⚙️ Configuration Options

Edit `config.json` to customize behavior:

| Key | Description | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather | *required* |
| `OPENAI_API_KEY` | Your OpenAI API key | *required* |
| `AUTHORIZED_USER_ID` | Your Telegram user ID | *required* |
| `AI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `SYSTEM_PROMPT` | AI personality/behavior instructions | Built-in prompt |
| `MAX_RETRIES` | How many times to retry failed API calls | `3` |

### Available AI Models

| Model | Speed | Cost | Quality |
|---|---|---|---|
| `gpt-4o-mini` | ⚡ Fast | 💚 Cheapest | ✅ Great |
| `gpt-4o` | 🔵 Medium | 💛 Moderate | ⭐ Best |
| `gpt-3.5-turbo` | ⚡ Fast | 💚 Cheap | 👍 Good |

---

## 🔄 Keeping the Bot Running in the Background

By default, the bot stops when you close Termux. Here are ways to keep it running:

### Option A — `nohup` (Simplest)

Run the bot detached from the terminal session:

```bash
nohup python main.py > agent.log 2>&1 &
echo "Bot PID: $!"
```

To stop it later:

```bash
kill $(pgrep -f main.py)
```

---

### Option B — `screen` (Recommended)

`screen` lets you detach and reattach to a running session.

```bash
# Install screen
pkg install screen -y

# Start a named screen session
screen -S ai-agent

# Run the bot inside the session
python main.py

# Detach from the session (bot keeps running)
# Press: Ctrl + A, then D

# Reattach later to see logs
screen -r ai-agent
```

---

### Option C — Termux:Boot (Auto-Start on Reboot)

Install [Termux:Boot](https://f-droid.org/packages/com.termux.boot/) from F-Droid.

```bash
# Create the boot scripts directory
mkdir -p ~/.termux/boot

# Create a startup script
nano ~/.termux/boot/start-ai-agent.sh
```

Paste this content:

```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/Termux-Telegram-AI-Agent
nohup python main.py > agent.log 2>&1 &
```

Make it executable:

```bash
chmod +x ~/.termux/boot/start-ai-agent.sh
```

Now the bot will start automatically every time your phone reboots.

---

### Keep Termux Awake (Important!)

Android aggressively kills background processes. To prevent this:

1. Go to Android **Settings → Battery**
2. Find **Termux** in the app list
3. Set battery optimization to **"Unrestricted"** or **"Don't optimize"**

You may also need to enable **"Allow background activity"** depending on your Android version.

---

## 📋 Viewing Logs

The bot logs all activity to both the terminal and `agent.log`:

```bash
# Watch live logs
tail -f agent.log

# View last 50 lines
tail -50 agent.log

# Search logs for errors
grep "ERROR" agent.log
```

---

## 🔧 Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'telegram'`
```bash
pip install -r requirements.txt
```

### ❌ `Config file not found: 'config.json'`
Make sure you're running `python main.py` from inside the project folder:
```bash
cd Termux-Telegram-AI-Agent
python main.py
```

### ❌ `Missing or unfilled config key: 'TELEGRAM_BOT_TOKEN'`
You haven't replaced the placeholder values in `config.json`. Open it and fill in your real keys:
```bash
nano config.json
```

### ❌ Bot not responding to messages
- Make sure the bot is running (you should see the banner in terminal)
- Confirm your `AUTHORIZED_USER_ID` matches the ID from @userinfobot
- Check that you're messaging the correct bot on Telegram

### ❌ `OpenAI API error: 401 Unauthorized`
Your `OPENAI_API_KEY` is wrong or expired. Get a new one at:
https://platform.openai.com/api-keys

### ❌ `OpenAI API error: 429 Rate limit exceeded`
- You've hit OpenAI's rate limit. Wait a moment and retry.
- Or upgrade your OpenAI plan at https://platform.openai.com

### ❌ Bot stops when I close Termux
Use the `screen` or `nohup` method described in the **Keeping the Bot Running** section above.

### ❌ Bot stops working after a few hours
Android killed the Termux process. Set battery optimization to **Unrestricted** for Termux (see above).

### ❌ `pip install` fails
Try updating pip first:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔐 Security Notes

- Your bot token and API key are stored **only** in `config.json` on your device
- The bot **ignores all messages** from anyone who isn't your `AUTHORIZED_USER_ID`
- Unauthorized access attempts are **logged** but never acknowledged to the attacker
- Never share your `config.json` or commit it to a public repository
- Add `config.json` to `.gitignore` if you fork this project

---

## 📊 Cost Estimate

Using `gpt-4o-mini` (the default):

| Usage | Estimated Cost |
|---|---|
| 100 messages/day | ~$0.01/day |
| 500 messages/day | ~$0.05/day |
| 1000 messages/day | ~$0.10/day |

These are rough estimates. Actual cost depends on message length.

---

## 🛠️ Customization Ideas

- **Change the AI personality** — edit `SYSTEM_PROMPT` in `config.json`
- **Use GPT-4o** for higher quality — change `AI_MODEL` to `gpt-4o`
- **Persistent memory** — extend the code to save history to a JSON file
- **Web search** — integrate a search API for real-time information
- **Voice messages** — add Whisper API for voice-to-text input
- **Image analysis** — use GPT-4o vision to describe photos you send

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgments

- [python-telegram-bot](https://python-telegram-bot.org/) — Telegram bot framework
- [OpenAI](https://openai.com) — AI API
- [Termux](https://termux.dev) — Android terminal emulator

---

<div align="center">

Built with ❤️ to run on your pocket computer

**⭐ Star this repo if it helped you!**

</div>
