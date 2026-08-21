from langchain_huggingface import HuggingFaceEmbeddings

from rag.chunker import create_chunks


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    encode_kwargs={"normalize_embeddings": True},
)


def create_embeddings():
    """
    Create embeddings for knowledge-base chunks.

    Returns:
        texts: list[str]
        vectors: list[list[float]]
    """

    chunks = create_chunks()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    vectors = embeddings.embed_documents(texts)

    return texts, vectors


if __name__ == "__main__":

    texts, vectors = create_embeddings()

    print(
        f"Created {len(texts)} embeddings "
        f"of dimension {len(vectors[0])}"
    )