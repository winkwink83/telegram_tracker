def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    text = text.strip()

    if not text:
        return []

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks

if __name__ == "__main__":
    text = "A" * 2500

    chunks = chunk_text(text)

    print(len(chunks))
    print(len(chunks[0]))
    print(len(chunks[1]))
    print(len(chunks[2]))