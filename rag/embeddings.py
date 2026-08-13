from sentence_transformers import SentenceTransformer

from rag.chunker import create_chunks


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings():
    """
    Build sentence-transformer embeddings for every chunk.

    Returns:
        texts: list[str]        - the chunk text, in the same order as embeddings
        embeddings: np.ndarray  - shape (num_chunks, embedding_dim)
    """
    chunks = create_chunks()

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return texts, embeddings


if __name__ == "__main__":
    texts, embeddings = create_embeddings()
    print(f"Created {len(texts)} embeddings of dimension {embeddings.shape[1]}")