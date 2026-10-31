
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Bot
from telegram.request import HTTPXRequest


# Locate the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load credentials from the project's .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")


async def send_telegram_message(message):

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise ValueError("Telegram credentials are missing!")

    request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=60,
        write_timeout=30,
        pool_timeout=30
    )

    bot = Bot(
        token=bot_token,
        request=request
    )

    async with bot:
        await bot.send_message(
            chat_id=chat_id,
            text=message
        )

    return "Telegram message sent successfully!"
