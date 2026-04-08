import asyncio
from telegram_tracker.client import connect_telegram


def main():
    asyncio.run(connect_telegram())


if __name__ == "__main__":
    main()