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

        for chunk in file_chunks:
            records.append({
                "text": chunk,
                "source_file": file_path.name,
            })

    return records


def rebuild_index() -> None:
    records = load_all_chunks()

    embeddings = [embed_text(record["text"]) for record in records]
    vectors = np.array(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(384)
    index.add(vectors)

    INDEX_DIR.mkdir(exist_ok=True)

    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))

    with open(INDEX_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"✅ Przebudowano indeks RAG: {len(records)} chunków")

def append_file_to_index(file_path: Path) -> None:
    INDEX_DIR.mkdir(exist_ok=True)

    index_path = INDEX_DIR / "index.faiss"
    metadata_path = INDEX_DIR / "metadata.json"

    text = file_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)

    new_records = [
        {
            "text": chunk,
            "source_file": file_path.name,
        }
        for chunk in chunks
    ]

    if not new_records:
        print(f"⚠️ Brak chunków w pliku: {file_path.name}")
        return

    embeddings = [embed_text(record["text"]) for record in new_records]
    vectors = np.array(embeddings, dtype="float32")

    if index_path.exists() and metadata_path.exists():
        index = faiss.read_index(str(index_path))

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        index = faiss.IndexFlatIP(384)
        metadata = []

    print(f"Przed add: {index.ntotal}")

    index.add(vectors)

    print(f"Po add: {index.ntotal}")

    metadata.extend(new_records)

    faiss.write_index(index, str(index_path))

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ Dopisano do indeksu: {len(new_records)} chunków z {file_path.name}")


if __name__ == "__main__":
    rebuild_index()