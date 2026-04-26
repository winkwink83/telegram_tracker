import argparse
import asyncio
from pathlib import Path

from telethon import TelegramClient

from telegram_tracker.config import API_ID, API_HASH


PROJECT_DIR = Path(__file__).resolve().parent
SESSION_FILE = PROJECT_DIR / "session"

ASSISTANT_PREFIX = "[ASYSTENT]"


def format_assistant_message(text: str) -> str:
    text = text.strip()

    if text.startswith(ASSISTANT_PREFIX):
        return text

    return f"{ASSISTANT_PREFIX} {text}"


async def send_message_to_self(text: str) -> None:
    message = format_assistant_message(text)

    async with TelegramClient(str(SESSION_FILE), API_ID, API_HASH) as client:
        await client.send_message("me", message)

    print(f"✅ Wysłano do Saved Messages: {message}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wyślij wiadomość do siebie na Telegramie z prefiksem [ASYSTENT]."
    )
    parser.add_argument(
        "message",
        nargs="+",
        help="Treść wiadomości do wysłania",
    )

    args = parser.parse_args()
    text = " ".join(args.message)

    asyncio.run(send_message_to_self(text))


if __name__ == "__main__":
    main()