import threading
from datetime import datetime

from telegram_tracker.bot_sender import send_message


def schedule_reminder(chat_id: int | str, remind_at: datetime, message: str) -> None:
    delay = (remind_at - datetime.now()).total_seconds()

    if delay < 0:
        delay = 0

    def job():
        send_message(chat_id, f"⏰ Przypomnienie:\n\n{message}")

    threading.Timer(delay, job).start()