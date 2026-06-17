import json
from pathlib import Path

import faiss
import numpy as np


from telegram_tracker.embeddings import embed_text


PROJECT_DIR = Path(__file__).resolve().parent
INDEX_DIR = PROJECT_DIR / "rag_index"


def search(query: str, k: int = 3) -> list[dict]:
    index = faiss.read_index(str(INDEX_DIR / "index.faiss"))

    with open(INDEX_DIR / "metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    query_vector = np.array(
        [embed_text(query)],
        dtype="float32"
    )

    scores, ids = index.search(query_vector, k)
    print("tutaj: ",(scores, ids))

    results = []

    for score, idx in zip(scores[0], ids[0]):
        results.append({
            "score": float(score),
            "text": metadata[idx]["text"],
            "source_file": metadata[idx]["source_file"],
        })

    return results


if __name__ == "__main__":
    results = search("Czy kupię drona?")

    for result in results:
        print()
        print(result["score"])
        print(result["text"])