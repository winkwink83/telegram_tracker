import json
from pathlib import Path

import faiss
import numpy as np

from telegram_tracker.chunking import chunk_text
from telegram_tracker.embeddings import embed_text


PROJECT_DIR = Path(__file__).resolve().parent
TRANSCRIPTS_DIR = PROJECT_DIR / "downloads" / "transcripts"
INDEX_DIR = PROJECT_DIR / "rag_index"


def load_all_chunks() -> list[dict]:
    records = []

    for file_path in sorted(TRANSCRIPTS_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")
        file_chunks = chunk_text(text)

        print(f"{file_path.name}: {len(file_chunks)} chunków")

        for chunk in file_chunks:
            records.append({
                "text": chunk,
                "source_file": file_path.name,
            })

    return records


if __name__ == "__main__":
    records = load_all_chunks()

    embeddings = [embed_text(record["text"]) for record in records]
    vectors = np.array(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(384)
    index.add(vectors)

    INDEX_DIR.mkdir(exist_ok=True)

    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))

    with open(INDEX_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Liczba chunków: {len(records)}")
    print(f"Liczba wektorów w FAISS: {index.ntotal}")
    print("Zapisano index.faiss")
    print("Zapisano metadata.json")