from telethon import TelegramClient
from telegram_tracker.config import API_ID, API_HASH


async def connect_telegram():
    client = TelegramClient("session", API_ID, API_HASH)

    await client.start()

    me = await client.get_me()
    print(f"✅ Połączono jako: {me.first_name}")

    await client.disconnect()