from pathlib import Path
from faster_whisper import WhisperModel

from telegram_tracker.reminder_parser import parse_reminder


def transcribe_voice(audio_path: Path, model: WhisperModel) -> str:
    segments, _info = model.transcribe(str(audio_path), language="pl")
    text = " ".join(segment.text.strip() for segment in segments).strip()

    if not text:
        return "[Brak rozpoznanego tekstu]"

    return text


def handle_voice(audio_path: Path, model: WhisperModel) -> dict:
    text = transcribe_voice(audio_path, model)

    reminder = parse_reminder(text)

    if reminder:
        return {
            "type": "reminder",
            "text": text,
            "remind_at": reminder["remind_at"],
            "message": reminder["message"],
        }

    return {
        "type": "transcript",
        "text": text,
    }