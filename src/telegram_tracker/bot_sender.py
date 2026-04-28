import argparse
from typing import Any

import requests

from telegram_tracker.config import ASSISTANT_PREFIX, BOT_TOKEN, DEFAULT_CHAT_ID


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
    parser.add_argument("message", nargs="+", help="Treść wiadomości")
    parser.add_argument(
        "--chat-id",
        help="ID czatu (opcjonalne, fallback na DEFAULT_CHAT_ID z .env)",
    )

    args = parser.parse_args()

    chat_id = args.chat_id or DEFAULT_CHAT_ID

    if not chat_id:
        raise RuntimeError("Brak chat_id. Podaj --chat-id albo ustaw DEFAULT_CHAT_ID w .env")

    text = " ".join(args.message)
    send_message(chat_id, text)

    print("✅ Wysłano")


if __name__ == "__main__":
    main()