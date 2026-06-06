import os

from dotenv import load_dotenv
import google.generativeai as genai

from telegram_tracker.retriever import search


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


SYSTEM_PROMPT = """
Jesteś osobistym asystentem użytkownika.

Odpowiadasz po polsku, krótko i konkretnie.
Masz odpowiadać wyłącznie na podstawie KONTEKSTU z notatek użytkownika.

Jeśli odpowiedzi nie ma w kontekście, powiedz:
"Nie widzę tego w notatkach."
"""


def build_context(results: list[dict]) -> str:
    context_parts = []

    for i, result in enumerate(results, start=1):
        context_parts.append(
            f"--- FRAGMENT {i} ({result['source_file']}) ---\n"
            f"{result['text']}"
        )

    return "\n\n".join(context_parts)


def ask_rag(question: str) -> str:
    results = search(question, k=3)

    if not results:
        return "Nie mam jeszcze żadnych zaindeksowanych notatek."

    context = build_context(results)

    prompt = f"""
{SYSTEM_PROMPT}

KONTEKST Z NOTATEK:
{context}

PYTANIE UŻYTKOWNIKA:
{question}

ODPOWIEDŹ:
"""

    response = model.generate_content(prompt)
    return response.text.strip()