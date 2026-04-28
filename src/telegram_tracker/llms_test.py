import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

chat = model.start_chat(history=[])


def main():
    print("LLM test (Gemini). Napisz 'exit', żeby wyjść.\n")

    while True:
        user = input("Ty: ").strip()

        if user.lower() in {"exit", "quit"}:
            break

        if not user:
            continue

        response = chat.send_message(user)
        print(f"\nAI: {response.text}\n")


if __name__ == "__main__":
    main()