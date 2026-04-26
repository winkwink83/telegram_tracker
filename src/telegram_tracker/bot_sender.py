import argparse
from typing import Any

import requests

from telegram_tracker.config import ASSISTANT_PREFIX, BOT_TOKEN


def format_assistant_message(text: str) -> str:
    text = text.strip()

    if text.startswith(ASSISTANT_PREFIX):
        return text

    return f"{ASSISTANT_PREFIX} {text}"


def telegram_api(method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    response = requests.post(url, json=payload or {}, timeout=60)
    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(data)

    return data


def send_message(chat_id: int | str, text: str) -> None:
    message = format_assistant_message(text)

    telegram_api(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": message,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wyślij wiadomość przez Telegram bota."
    )
    parser.add_argument("chat_id", help="ID czatu, do którego wysłać wiadomość")
    parser.add_argument("message", nargs="+", help="Treść wiadomości")

    args = parser.parse_args()

    text = " ".join(args.message)
    send_message(args.chat_id, text)

    print("✅ Wysłano")


if __name__ == "__main__":
    main()