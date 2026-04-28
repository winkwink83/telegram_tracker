import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent / "downloads"
REMINDERS_FILE = BASE_DIR / "reminders.json"


def save_reminder(chat_id: int | str, remind_at: datetime, message: str) -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    reminders = []

    if REMINDERS_FILE.exists():
        reminders = json.loads(REMINDERS_FILE.read_text(encoding="utf-8"))

    reminders.append(
        {
            "chat_id": chat_id,
            "remind_at": remind_at.isoformat(),
            "message": message,
            "sent": False,
        }
    )

    REMINDERS_FILE.write_text(
        json.dumps(reminders, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )