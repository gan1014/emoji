import os
from telegram import Bot


async def send_telegram_message(message):

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise ValueError("Telegram credentials are missing!")

    bot = Bot(token=bot_token)

    async with bot:
        await bot.send_message(
            chat_id=chat_id,
            text=message
        )

    return "Telegram message sent successfully!"