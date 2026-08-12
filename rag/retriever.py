import numpy as np
from sentence_transformers import SentenceTransformer
from rag.vector_store import load_vector_store

model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(query, top_k=3, threshold=0.45):

    chunks, embeddings = load_vector_store()

    # Normalize document embeddings
    embeddings = embeddings / np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True
    )

    # Encode question
    query_embedding = model.encode(query).flatten()

    query_embedding = query_embedding / np.linalg.norm(
        query_embedding
    )

    # Calculate similarity
    scores = np.dot(
        embeddings,
        query_embedding
    )

    # Best results
    top_indices = np.argsort(scores)[-top_k:][::-1]

    results = []

    for index in top_indices:

        score = scores[index]

        # Ignore unrelated questions
        if score >= threshold:

            results.append({
                "chunks": chunks[index],
                "score": float(score)
            })

    return results


if __name__ == "__main__":

    question = input("Enter your question: ")

    results = retrieve(question)

    print("\nRelevant Chunks:")
    print("================")

    if not results:
        print("No relevant AppInSnap information found.")

    for result in results:

        print(f"\nScore: {result['score']:.4f}")
        print(result["chunks"])
        print("\n----------------")