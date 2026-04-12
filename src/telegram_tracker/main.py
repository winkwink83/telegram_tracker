import asyncio

from telegram_tracker.client import watch_saved_voices_forever


def main():
    asyncio.run(watch_saved_voices_forever())


if __name__ == "__main__":
    main()