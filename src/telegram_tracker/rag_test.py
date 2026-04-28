import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai


PROJECT_DIR = Path(__file__).resolve().parent
TRANSCRIPTS_DIR = PROJECT_DIR / "downloads" / "transcripts"

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


SYSTEM_PROMPT = """
Jesteś osobistym asystentem użytkownika.

Odpowiadasz po polsku, krótko i konkretnie.
Masz odpowiadać głównie na podstawie NOTATEK użytkownika.

Jeśli odpowiedzi nie ma w notatkach, powiedz:
"Nie widzę tego w notatkach."
"""


def load_notes() -> str:
    if not TRANSCRIPTS_DIR.exists():
        return ""

    notes = []

    for file_path in sorted(TRANSCRIPTS_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if text:
            notes.append(
                f"--- NOTATKA: {file_path.name} ---\n{text}"
            )

    return "\n\n".join(notes)


def ask_llm(question: str, notes: str) -> str:
    prompt = f"""
{SYSTEM_PROMPT}

NOTATKI:
{notes}

PYTANIE UŻYTKOWNIKA:
{question}

ODPOWIEDŹ:
"""

    response = model.generate_content(prompt)
    return response.text.strip()


def main() -> None:
    notes = load_notes()

    if not notes:
        print("Brak notatek w downloads/transcripts")
        return

    print("RAG test działa. Napisz 'exit', żeby wyjść.\n")
    print(f"Wczytano notatki z: {TRANSCRIPTS_DIR}\n")

    while True:
        question = input("Ty: ").strip()

        if question.lower() in {"exit", "quit", "q"}:
            break

        if not question:
            continue

        answer = ask_llm(question, notes)
        print(f"\nAI: {answer}\n")


if __name__ == "__main__":
    main()