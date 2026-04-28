from telegram_tracker.rag_engine import ask_rag


def main() -> None:
    print("RAG test działa. Napisz 'exit', żeby wyjść.\n")

    while True:
        question = input("Ty: ").strip()

        if question.lower() in {"exit", "quit", "q"}:
            break

        if not question:
            continue

        try:
            answer = ask_rag(question)
            print(f"\nAI: {answer}\n")
        except Exception as exc:
            print(f"\n❌ Błąd: {exc}\n")


if __name__ == "__main__":
    main()