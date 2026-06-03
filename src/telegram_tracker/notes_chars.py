from pathlib import Path


TRANSCRIPTS_DIR = Path(
    r"C:\Users\macie\Desktop\Projekty\telegram_tracker\src\telegram_tracker\downloads\transcripts"
)

files = sorted(TRANSCRIPTS_DIR.glob("*.txt"))[-10:]

total_chars = 0

for file_path in files:
    text = file_path.read_text(encoding="utf-8")
    total_chars += len(text)

print(f"Łącznie znaków: {total_chars:,}")
print(f"Przybliżona liczba tokenów: {total_chars // 4:,}")