from sentence_transformers import SentenceTransformer
from rag.vector_store import client, COLLECTION_NAME


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def retrieve(query, top_k=5, threshold=0.45):

    # Convert question into embedding
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    # Search Qdrant
    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=top_k
    )

    results = []

    for point in result.points:

        score = point.score

        if score >= threshold:

            results.append({
                "chunks": point.payload["text"],
                "score": float(score)
            })

    return results


if __name__ == "__main__":

    question = input("Enter your question: ")

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