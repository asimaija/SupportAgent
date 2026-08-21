import atexit

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain_qdrant import QdrantVectorStore

from rag.chunker import create_chunks
from rag.embeddings import embeddings


COLLECTION_NAME = "appinsnap"

# All-MiniLM-L6-v2 output size — used to create the Qdrant collection
# the first time, before any vectors exist to infer it from.
EMBEDDING_DIM = 384


# --------------------------------
# Connect to local Qdrant storage
#
# One shared client for the whole process (ingestion AND retrieval),
# since a local, file-based Qdrant store can only be opened by one
# client at a time. rag/retriever.py imports this same `client`.
# --------------------------------

client = QdrantClient(
    path="./qdrant_db"
)


# --------------------------------
# Close Qdrant cleanly
# --------------------------------

atexit.register(client.close)


def _ensure_collection():

    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )


def get_vector_store():
    """
    Returns a LangChain QdrantVectorStore bound to the AppInSnap
    collection. content_payload_key="text" matches the payload key
    already used by points ingested before this migrated to
    LangChain, so existing data keeps working without re-ingesting.
    """

    _ensure_collection()

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
        content_payload_key="text",
        distance=Distance.COSINE,
    )


def create_vector_store():
    """
    Ingestion: chunk the knowledge base, then hand the chunks to
    LangChain's QdrantVectorStore.add_texts(), which embeds them
    (via rag/embeddings.py) and upserts them into Qdrant — the same
    two steps the old manual PointStruct code did by hand.
    """

    chunks = create_chunks()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    store = get_vector_store()

    store.add_texts(texts)

    print(
        "Qdrant vector store created successfully!"
    )

    print(
        "Total chunks:",
        len(texts)
    )


if __name__ == "__main__":

    create_vector_store()