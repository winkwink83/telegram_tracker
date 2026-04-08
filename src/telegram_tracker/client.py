from pathlib import Path

from telethon import TelegramClient
from telegram_tracker.config import API_ID, API_HASH


DOWNLOAD_DIR = Path("downloads/voice")


async def download_saved_voices():
    client = TelegramClient("session", API_ID, API_HASH)

    await client.start()

    me = await client.get_me()
    print(f"✅ Połączono jako: {me.first_name}")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Folder pobierania: {DOWNLOAD_DIR.resolve()}\n")

    downloaded = 0

    async for message in client.iter_messages("me", limit=10):
        if message.voice:
            file_path = await message.download_media(file=str(DOWNLOAD_DIR))
            downloaded += 1
            print(f"🎤 Pobrano głosówkę ID={message.id} -> {file_path}")

    if downloaded == 0:
        print("Brak głosówek do pobrania.")
    else:
        print(f"\n✅ Pobrano {downloaded} głosówek.")

    await client.disconnect()