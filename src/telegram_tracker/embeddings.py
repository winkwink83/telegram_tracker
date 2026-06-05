from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

_model = SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    return _model.encode(
        text,
        normalize_embeddings=True
    ).tolist()

if __name__ == "__main__":
    print(len(embed_text("Muszę kupić mleko")))