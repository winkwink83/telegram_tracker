import asyncio

from telegram_tracker.client import download_and_transcribe_saved_voices


def main():
    asyncio.run(download_and_transcribe_saved_voices())


if __name__ == "__main__":
    main()