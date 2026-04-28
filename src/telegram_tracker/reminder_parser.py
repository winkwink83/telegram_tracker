from datetime import datetime, timedelta
import re


def parse_reminder(text: str) -> dict | None:
    normalized = text.lower().strip()

    if "przypomnij" not in normalized:
        return None

    time_match = re.search(r"za\s+(\d+)\s+minut", normalized)

    if not time_match:
        return None

    minutes = int(time_match.group(1))
    remind_at = datetime.now() + timedelta(minutes=minutes)

    message_match = re.search(r"(?:żeby|zeby|żebym|zebym)\s+(.+)", normalized)

    if message_match:
        message = message_match.group(1).strip()
    else:
        message = normalized

    message = message.rstrip(".")

    return {
        "remind_at": remind_at,
        "message": message,
    }