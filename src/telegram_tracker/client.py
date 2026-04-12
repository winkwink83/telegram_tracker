from pathlib import Path

from telethon import TelegramClient
from faster_whisper import WhisperModel

from telegram_tracker.config import API_ID, API_HASH


DOWNLOAD_DIR = Path("downloads/voice")
TRANSCRIPTS_DIR = Path("downloads/transcripts")


async def download_and_transcribe_saved_voices():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()

    print("✅ Połączono z Telegramem")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    print("⏳ Ładowanie modelu...")
    model = WhisperModel("base", device="cpu", compute_type="int8")

    found_any_voice = False

    async for message in client.iter_messages("me", limit=20):
        if not message.voice:
            continue

        found_any_voice = True

        timestamp = message.date.astimezone().strftime("%Y-%m-%d_%H-%M-%S")
        audio_file_path = DOWNLOAD_DIR / f"{timestamp}_{message.id}.oga"
        transcript_file_path = TRANSCRIPTS_DIR / f"{timestamp}_{message.id}.txt"

        print(f"\n🎤 Głosówka ID={message.id}")

        if audio_file_path.exists():
            print(f"⏭️ Głosówka już istnieje: {audio_file_path.name}")
        else:
            downloaded_path = await message.download_media(file=str(audio_file_path))
            print(f"📥 Pobrano: {downloaded_path}")

        if transcript_file_path.exists():
            print(f"⏭️ Transkrypcja już istnieje: {transcript_file_path.name}")
            continue

        print("🧠 Transkrypcja w toku...")

        segments, info = model.transcribe(str(audio_file_path), language="pl")
        text = " ".join(segment.text.strip() for segment in segments).strip()

        if not text:
            text = "[Brak rozpoznanego tekstu]"

        transcript_file_path.write_text(text, encoding="utf-8")

        print(f"📝 Tekst: {text}")
        print(f"💾 Zapisano transkrypcję: {transcript_file_path}")

    if not found_any_voice:
        print("Brak głosówek w ostatnich 20 wiadomościach Saved Messages.")

    await client.disconnect()