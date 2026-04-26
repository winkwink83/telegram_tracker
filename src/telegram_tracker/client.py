import json
import time
from pathlib import Path
from typing import Any

import requests
from faster_whisper import WhisperModel

from telegram_tracker.bot_sender import send_message, telegram_api
from telegram_tracker.config import BOT_TOKEN


PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR / "downloads"
DOWNLOAD_DIR = BASE_DIR / "voice"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
STATE_FILE = BASE_DIR / "state.json"


def ensure_directories() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def load_last_update_id() -> int:
    if not STATE_FILE.exists():
        return 0

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return int(data.get("last_update_id", 0))
    except Exception:
        print("⚠️ Nie udało się wczytać state.json, startuję od zera.")
        return 0


def save_last_update_id(update_id: int) -> None:
    payload = {"last_update_id": update_id}

    STATE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def download_file(file_id: str, target_path: Path) -> None:
    file_info = telegram_api("getFile", {"file_id": file_id})
    file_path = file_info["result"]["file_path"]

    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    target_path.write_bytes(response.content)


def transcribe_voice(audio_path: Path, model: WhisperModel) -> str:
    segments, _info = model.transcribe(str(audio_path), language="pl")
    text = " ".join(segment.text.strip() for segment in segments).strip()

    if not text:
        return "[Brak rozpoznanego tekstu]"

    return text


def process_voice_message(message: dict[str, Any], model: WhisperModel) -> None:
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    voice = message["voice"]

    file_id = voice["file_id"]
    timestamp = message.get("date", int(time.time()))

    audio_file_path = DOWNLOAD_DIR / f"{timestamp}_{message_id}.oga"
    transcript_file_path = TRANSCRIPTS_DIR / f"{timestamp}_{message_id}.txt"

    print(f"\n🎤 Głosówka chat_id={chat_id}, message_id={message_id}")

    if not audio_file_path.exists():
        print("📥 Pobieram audio...")
        download_file(file_id, audio_file_path)
        print(f"✅ Pobrano: {audio_file_path.name}")

    print("🧠 Transkrypcja w toku...")
    text = transcribe_voice(audio_file_path, model)

    transcript_file_path.write_text(text, encoding="utf-8")

    print(f"📝 Tekst: {text}")
    print(f"💾 Zapisano: {transcript_file_path.name}")

    send_message(chat_id, f"Transkrypcja:\n\n{text}")


def process_text_message(message: dict[str, Any]) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if not text:
        return

    if text == "/start":
        send_message(
            chat_id,
            "Bot działa. Wyślij głosówkę, a zrobię transkrypcję."
        )
        return

    send_message(
        chat_id,
        f"Odebrałem tekst:\n\n{text}"
    )


def handle_update(update: dict[str, Any], model: WhisperModel) -> None:
    message = update.get("message")

    if not message:
        return

    if "voice" in message:
        process_voice_message(message, model)
        return

    if "text" in message:
        process_text_message(message)
        return


def watch_bot_forever() -> None:
    ensure_directories()

    last_update_id = load_last_update_id()

    print("⏳ Ładowanie modelu Whisper...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("✅ Model gotowy")

    print("🤖 Bot nasłuchuje. Wyślij głosówkę do bota.")

    while True:
        try:
            data = telegram_api(
                "getUpdates",
                {
                    "offset": last_update_id + 1,
                    "timeout": 5,
                    "allowed_updates": ["message"],
                },
            )

            updates = data.get("result", [])

            for update in updates:
                update_id = update["update_id"]

                try:
                    handle_update(update, model)
                except Exception as exc:
                    print(f"❌ Błąd przy update_id={update_id}: {exc}")

                last_update_id = update_id
                save_last_update_id(last_update_id)

        except KeyboardInterrupt:
            print("\n👋 Zatrzymano bota.")
            break

        except Exception as exc:
            print(f"❌ Błąd pętli bota: {exc}")
            time.sleep(5)