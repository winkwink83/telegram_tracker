from pathlib import Path
from faster_whisper import WhisperModel


def transcribe_voice(audio_path: Path, model: WhisperModel) -> str:
    segments, _info = model.transcribe(str(audio_path), language="pl")
    text = " ".join(segment.text.strip() for segment in segments).strip()

    if not text:
        return "[Brak rozpoznanego tekstu]"

    return text


def handle_voice(audio_path: Path, model: WhisperModel) -> dict:
    text = transcribe_voice(audio_path, model)

    return {
        "type": "transcript",
        "text": text,
    }