import faiss
import numpy as np

from telegram_tracker.embeddings import embed_text


def create_index() -> faiss.Index:
    return faiss.IndexFlatIP(384)


if __name__ == "__main__":
    index = create_index()

    document_embedding = embed_text("Muszę kupić mleko")
    document_vector = np.array([document_embedding], dtype="float32")

    index.add(document_vector)

    query_embedding = embed_text("Trzeba kupić mleko")
    query_vector = np.array([query_embedding], dtype="float32")

    scores, ids = index.search(query_vector, k=1)

    print("Liczba wektorów w indeksie:", index.ntotal)
    print("Wynik podobieństwa:", scores)
    print("ID znalezionego wektora:", ids)