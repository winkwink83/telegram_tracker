from datetime import datetime


def print_timestamp() -> None:
    now = datetime.now()

    timestamp = int(now.timestamp())
    formatted_date = now.strftime("%d-%m-%Y %H:%M:%S")

    print(f"Timestamp: {timestamp}")
    print(f"Data: {formatted_date}")


def main() -> None:
    print_timestamp()


if __name__ == "__main__":
    main()