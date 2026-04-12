import asyncio
import json
from pathlib import Path
from typing import Set

from telethon import TelegramClient, events
from faster_whisper import WhisperModel

from telegram_tracker.config import API_ID, API_HASH


PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR / "downloads"
DOWNLOAD_DIR = BASE_DIR / "voice"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
STATE_FILE = BASE_DIR / "state.json"


def ensure_directories() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def load_processed_ids() -> Set[int]:
    if not STATE_FILE.exists():
        return set()

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {int(x) for x in data.get("processed_message_ids", [])}
    except Exception:
        print("⚠️ Nie udało się wczytać state.json, startuję z pustym stanem.")
        return set()


def save_processed_ids(processed_ids: Set[int]) -> None:
    payload = {
        "processed_message_ids": sorted(processed_ids)
    }
    STATE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def process_voice_message(message, model: WhisperModel, processed_ids: Set[int]) -> None:
    if message.id in processed_ids:
        print(f"⏭️ Wiadomość ID={message.id} już była przetworzona")
        return

    if not message.voice:
        return

    timestamp = message.date.astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    audio_file_path = DOWNLOAD_DIR / f"{timestamp}_{message.id}.oga"
    transcript_file_path = TRANSCRIPTS_DIR / f"{timestamp}_{message.id}.txt"

    print(f"\n🎤 Głosówka ID={message.id}")

    if not audio_file_path.exists():
        downloaded_path = await message.download_media(file=str(audio_file_path))
        print(f"📥 Pobrano: {downloaded_path}")
    else:
        print(f"⏭️ Audio już istnieje: {audio_file_path.name}")

    if transcript_file_path.exists():
        print(f"⏭️ Transkrypcja już istnieje: {transcript_file_path.name}")
        processed_ids.add(message.id)
        save_processed_ids(processed_ids)
        return

    print("🧠 Transkrypcja w toku...")
    segments, _info = model.transcribe(str(audio_file_path), language="pl")
    text = " ".join(segment.text.strip() for segment in segments).strip()

    if not text:
        text = "[Brak rozpoznanego tekstu]"

    transcript_file_path.write_text(text, encoding="utf-8")

    processed_ids.add(message.id)
    save_processed_ids(processed_ids)

    print(f"📝 Tekst: {text}")
    print(f"💾 Zapisano transkrypcję: {transcript_file_path}")


async def catch_up_existing_voices(client: TelegramClient, model: WhisperModel, processed_ids: Set[int], limit: int = 50) -> None:
    to_process = []

    async for message in client.iter_messages("me", limit=limit):
        if message.voice and message.id not in processed_ids:
            to_process.append(message)

    to_process.reverse()

    for message in to_process:
        try:
            await process_voice_message(message, model, processed_ids)
        except Exception as exc:
            print(f"❌ Błąd przy backlogu ID={message.id}: {exc}")


async def watch_saved_voices_forever() -> None:
    ensure_directories()
    processed_ids = load_processed_ids()

    print("⏳ Ładowanie modelu Whisper...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("✅ Model gotowy")

    client = TelegramClient("session", API_ID, API_HASH)

    @client.on(events.NewMessage(chats="me"))
    async def handler(event):
        message = event.message

        if not message.voice:
            return

        try:
            await process_voice_message(message, model, processed_ids)
        except Exception as exc:
            print(f"❌ Błąd przy nowej głosówce ID={message.id}: {exc}")

    print("🔌 Łączenie z Telegramem...")
    await client.start()
    print("✅ Połączono z Telegramem")

    print("🔎 Obrabiam zaległe głosówki...")
    await catch_up_existing_voices(client, model, processed_ids, limit=50)

    print("👂 Nasłuch aktywny. Czekam na nowe głosówki w Saved Messages...")

    await client.run_until_disconnected()