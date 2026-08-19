from sentence_transformers import SentenceTransformer

from rag.vector_store import (
    client,
    COLLECTION_NAME,
)


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def retrieve(
    query,
    top_k=5,
    threshold=0.45,
):
    """
    Retrieve relevant knowledge-base chunks.

    The user's question embedding is temporary.
    It is NOT stored in Qdrant.
    """

    # --------------------------------
    # 1. Create temporary query embedding
    # --------------------------------

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    # --------------------------------
    # 2. Search existing embeddings
    # --------------------------------

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=top_k,
    )

    # --------------------------------
    # 3. Collect relevant chunks
    # --------------------------------

    results = []

    for point in result.points:

        score = point.score

        if score >= threshold:

            results.append({
                "chunks": point.payload["text"],
                "score": float(score),
            })

    # --------------------------------
    # 4. Return results
    # --------------------------------

    return results


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    )

    results = retrieve(question)

    print("\nRelevant Chunks:")
    print("================")

    if not results:

        print(
            "No relevant AppInSnap information found."
        )

    for result in results:

        print(
            f"\nScore: {result['score']:.4f}"
        )

        print(result["chunks"])

        print("\n----------------")