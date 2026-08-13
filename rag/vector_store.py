import atexit

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from rag.embeddings import create_embeddings


COLLECTION_NAME = "appinsnap"

# Connect to local Qdrant storage (file-based, no server needed)
client = QdrantClient(
    path="./qdrant_db"
)

# Ensure the client is closed cleanly before interpreter shutdown,
# so QdrantClient.__del__ has nothing left to clean up
atexit.register(client.close)


def create_vector_store():

    chunks, embeddings = create_embeddings()

    # Create collection if it doesn't exist
    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=embeddings.shape[1],
                distance=Distance.COSINE
            )
        )

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
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print("Qdrant vector store created successfully!")
    print("Total chunks:", len(chunks))


if __name__ == "__main__":

    create_vector_store()