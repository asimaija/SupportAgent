import atexit

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from rag.embeddings import create_embeddings


COLLECTION_NAME = "appinsnap"


# --------------------------------
# Connect to local Qdrant storage
# --------------------------------

client = QdrantClient(
    path="./qdrant_db"
)


# --------------------------------
# Close Qdrant cleanly
# --------------------------------

atexit.register(client.close)


def create_vector_store():

    # Create embeddings for knowledge-base chunks
    chunks, embeddings = create_embeddings()

    # --------------------------------
    # Create collection
    # --------------------------------

    if not client.collection_exists(
        COLLECTION_NAME
    ):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=embeddings.shape[1],
                distance=Distance.COSINE,
            ),
        )

    # --------------------------------
    # Create Qdrant points
    # --------------------------------

    points = []

    for i, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        points.append(
            PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "text": chunk
                },
            )
        )

    # --------------------------------
    # Store ONLY knowledge-base chunks
    # --------------------------------

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print(
        "Qdrant vector store created successfully!"
    )

    print(
        "Total chunks:",
        len(chunks)
    )


if __name__ == "__main__":

    create_vector_store()