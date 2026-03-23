"""
╔══════════════════════════════════════════════════════════╗
║         Termux Telegram AI Agent — main.py               ║
║         Runs on Android via Termux                       ║
║         Telegram Bot + OpenAI API integration            ║
╚══════════════════════════════════════════════════════════╝
"""

import json
import logging
import asyncio
import sys
import os
from datetime import datetime

from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode, ChatAction

# ──────────────────────────────────────────────
# 1. LOGGING SETUP
# ──────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# 2. CONFIG LOADER
# ──────────────────────────────────────────────

def load_config(path: str = "config.json") -> dict:
    """
    Load configuration from config.json.
    Exits with a clear error if the file is missing or malformed.
    """
    if not os.path.exists(path):
        logger.critical(f"Config file not found: '{path}'")
        logger.critical("Copy config.json, fill in your keys, and restart.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    required_keys = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "AUTHORIZED_USER_ID"]
    for key in required_keys:
        value = config.get(key, "")
        if not value or "YOUR_" in str(value):
            logger.critical(f"Missing or unfilled config key: '{key}'")
            logger.critical(f"Please set '{key}' in config.json before running.")
            sys.exit(1)

    return config


# ──────────────────────────────────────────────
# 3. LOAD CONFIG + INIT CLIENTS
# ──────────────────────────────────────────────

config = load_config()

TELEGRAM_BOT_TOKEN   = config["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY       = config["OPENAI_API_KEY"]
AUTHORIZED_USER_ID   = int(config["AUTHORIZED_USER_ID"])
AI_MODEL             = config.get("AI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT        = config.get(
    "SYSTEM_PROMPT",
    "You are a helpful, concise, and smart AI assistant running on an Android phone via Termux. "
    "Keep responses clear and well-structured."
)
MAX_RETRIES          = int(config.get("MAX_RETRIES", 3))
MAX_MESSAGE_LENGTH   = 4000  # Telegram's limit is 4096 chars

# OpenAI async client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Per-user conversation history stored in memory
# Format: { user_id: [{"role": "...", "content": "..."}] }
conversation_history: dict[int, list] = {}


# ──────────────────────────────────────────────
# 4. AUTHORIZATION GUARD
# ──────────────────────────────────────────────

def is_authorized(user_id: int) -> bool:
    """Return True only if the sender is the authorized user."""
    return user_id == AUTHORIZED_USER_ID


def unauthorized_response(update: Update) -> None:
    """Log and silently reject unauthorized access attempts."""
    user = update.effective_user
    logger.warning(
        f"UNAUTHORIZED access attempt — ID: {user.id}, "
        f"Name: {user.full_name}, Username: @{user.username}"
    )


# ──────────────────────────────────────────────
# 5. AI REQUEST FUNCTION
# ──────────────────────────────────────────────

async def get_ai_response(user_id: int, user_message: str) -> str:
    """
    Send the user message to OpenAI and return the AI reply.
    Maintains per-user conversation history for context.
    Retries up to MAX_RETRIES times on failure.
    """

    # Initialize history for new user session
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Append the new user message to history
    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Build messages array: system prompt + history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[user_id]

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"OpenAI request — model: {AI_MODEL}, attempt: {attempt}/{MAX_RETRIES}")

            response = await openai_client.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
            )

            ai_reply = response.choices[0].message.content.strip()

            # Save assistant reply to history for future context
            conversation_history[user_id].append({
                "role": "assistant",
                "content": ai_reply
            })

            # Trim history if it grows too large (keep last 20 exchanges)
            if len(conversation_history[user_id]) > 40:
                conversation_history[user_id] = conversation_history[user_id][-40:]

            logger.info(f"AI response received — {len(ai_reply)} chars")
            return ai_reply

        except Exception as e:
            last_error = str(e)
            logger.error(f"OpenAI API error (attempt {attempt}): {last_error}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 * attempt)  # Exponential back-off

    # All retries failed — remove the user message we added to history
    conversation_history[user_id].pop()
    return f"⚠️ AI request failed after {MAX_RETRIES} attempts.\n\nError: `{last_error}`"


# ──────────────────────────────────────────────
# 6. COMMAND HANDLERS
# ──────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command — welcome message."""
    user = update.effective_user

    if not is_authorized(user.id):
        unauthorized_response(update)
        return

    logger.info(f"/start called by {user.full_name} ({user.id})")

    welcome = (
        f"👋 *Hello, {user.first_name}!*\n\n"
        "Your private AI agent is online and ready.\n\n"
        "Just type any message and I'll respond using AI.\n\n"
        "📋 *Available commands:*\n"
        "• `/start` — Show this message\n"
        "• `/help` — Usage guide\n"
        "• `/status` — System status\n"
        "• `/clear` — Clear conversation history\n"
        "• `/about` — About this agent\n\n"
        "_Powered by OpenAI • Running on Termux_"
    )

    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    user = update.effective_user

    if not is_authorized(user.id):
        unauthorized_response(update)
        return

    help_text = (
        "🤖 *AI Agent Help*\n\n"
        "*How to use:*\n"
        "Simply type any message and the AI will respond.\n\n"
        "*Commands:*\n"
        "• `/start` — Welcome screen\n"
        "• `/help` — This help message\n"
        "• `/status` — Show agent status & stats\n"
        "• `/clear` — Wipe conversation memory\n"
        "• `/about` — About this project\n\n"
        "*Tips:*\n"
        "• The agent remembers context within your session\n"
        "• Use `/clear` to start a fresh conversation\n"
        "• Long responses are split automatically\n\n"
        "*Model:* `" + AI_MODEL + "`"
    )

    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command — show system info."""
    user = update.effective_user

    if not is_authorized(user.id):
        unauthorized_response(update)
        return

    user_id = user.id
    history_length = len(conversation_history.get(user_id, []))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status_text = (
        "📊 *Agent Status*\n\n"
        f"🟢 *Status:* Online\n"
        f"🕐 *Time:* `{now}`\n"
        f"🤖 *AI Model:* `{AI_MODEL}`\n"
        f"💬 *Messages in memory:* {history_length}\n"
        f"🔁 *Max retries:* {MAX_RETRIES}\n"
        f"🆔 *Your user ID:* `{user_id}`\n"
    )

    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /clear command — wipe conversation history."""
    user = update.effective_user

    if not is_authorized(user.id):
        unauthorized_response(update)
        return

    conversation_history[user.id] = []
    logger.info(f"Conversation history cleared for user {user.id}")
    await update.message.reply_text(
        "🧹 *Conversation cleared!*\nStarting fresh — what's on your mind?",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /about command."""
    user = update.effective_user

    if not is_authorized(user.id):
        unauthorized_response(update)
        return

    about_text = (
        "🤖 *Termux Telegram AI Agent*\n\n"
        "A private AI assistant that runs on your Android phone "
        "inside Termux and is controlled via Telegram.\n\n"
        "📦 *Stack:*\n"
        "• Python 3 (Termux)\n"
        "• python-telegram-bot\n"
        "• OpenAI API\n\n"
        "🔒 *Security:*\n"
        "• Single authorized user\n"
        "• No data stored externally\n\n"
        "🔗 *GitHub:*\n"
        "`github.com/your-username/Termux-Telegram-AI-Agent`"
    )

    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)


# ──────────────────────────────────────────────
# 7. MAIN MESSAGE HANDLER
# ──────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Core message handler — receives user text, calls AI, sends reply.
    Shows a 'Thinking...' message while waiting for the AI response.
    Handles long messages by splitting them.
    """
    user = update.effective_user
    user_message = update.message.text

    # Block unauthorized users
    if not is_authorized(user.id):
        unauthorized_response(update)
        return

    logger.info(f"Message from {user.full_name} ({user.id}): {user_message[:80]}...")

    # Show "typing..." indicator in Telegram
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # Send a "Thinking..." placeholder message
    thinking_msg = await update.message.reply_text("🤔 *Thinking...*", parse_mode=ParseMode.MARKDOWN)

    # Get AI response
    ai_reply = await get_ai_response(user.id, user_message)

    # Delete the "Thinking..." message
    try:
        await thinking_msg.delete()
    except Exception:
        pass  # If deletion fails, just continue

    # Split and send response (Telegram has a 4096 char limit)
    await send_long_message(update, ai_reply)


async def send_long_message(update: Update, text: str) -> None:
    """
    Split a long message into chunks and send each as a separate message.
    Tries Markdown first; falls back to plain text if parsing fails.
    """
    chunks = split_message(text, MAX_MESSAGE_LENGTH)

    for i, chunk in enumerate(chunks):
        # Add part indicator for multi-chunk messages
        if len(chunks) > 1:
            chunk = f"*[{i+1}/{len(chunks)}]*\n\n{chunk}"

        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # Fallback: send as plain text if Markdown causes issues
            try:
                await update.message.reply_text(chunk)
            except Exception as e:
                logger.error(f"Failed to send message chunk {i+1}: {e}")


def split_message(text: str, max_length: int) -> list[str]:
    """
    Split a long text string into chunks of at most max_length characters.
    Tries to split on newlines for cleaner breaks.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    while len(text) > max_length:
        # Try to break on a newline near the limit
        split_pos = text.rfind("\n", 0, max_length)
        if split_pos == -1 or split_pos < max_length // 2:
            split_pos = max_length

        chunks.append(text[:split_pos].strip())
        text = text[split_pos:].strip()

    if text:
        chunks.append(text)

    return chunks


# ──────────────────────────────────────────────
# 8. ERROR HANDLER
# ──────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Telegram errors and notify the user if possible."""
    logger.error(f"Telegram error: {context.error}", exc_info=context.error)

    if isinstance(update, Update) and update.message:
        try:
            await update.message.reply_text(
                "⚠️ An internal error occurred. Please try again.",
            )
        except Exception:
            pass


# ──────────────────────────────────────────────
# 9. STARTUP BANNER
# ──────────────────────────────────────────────

def print_banner() -> None:
    """Print a startup banner to the terminal."""
    print("\n" + "═" * 55)
    print("  🤖  Termux Telegram AI Agent")
    print("═" * 55)
    print(f"  Model       : {AI_MODEL}")
    print(f"  Auth User   : {AUTHORIZED_USER_ID}")
    print(f"  Max Retries : {MAX_RETRIES}")
    print(f"  Started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 55)
    print("  Polling for messages... (Ctrl+C to stop)\n")


# ──────────────────────────────────────────────
# 10. MAIN ENTRY POINT
# ──────────────────────────────────────────────

def main() -> None:
    """
    Build and start the Telegram bot application.
    Registers all command and message handlers, then begins polling.
    """
    print_banner()

    # Build the Application using the bot token
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("help",   cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("clear",  cmd_clear))
    app.add_handler(CommandHandler("about",  cmd_about))

    # Register message handler (all non-command text messages)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register global error handler
    app.add_error_handler(error_handler)

    logger.info("Bot started — polling for updates.")

    # Start polling (blocking)
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,   # Ignore messages sent while bot was offline
    )


if __name__ == "__main__":
    main()
