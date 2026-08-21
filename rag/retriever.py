from rag.vector_store import get_vector_store


def retrieve(
    query,
    top_k=5,
    threshold=0.45,
):
    """
    Retrieve relevant knowledge-base chunks.

    The user's question embedding is temporary — created in memory by
    LangChain's QdrantVectorStore (via rag/embeddings.py) purely to
    run this search. It is NOT stored in Qdrant.
    """

    store = get_vector_store()

    # --------------------------------
    # LangChain does the embedding + search + score-filtering in one
    # call: store.similarity_search_with_score() embeds `query` with
    # the shared HuggingFaceEmbeddings instance, searches Qdrant, and
    # score_threshold drops anything below our confidence bar before
    # it even comes back — this is the same hard gate the old manual
    # "if score >= threshold" loop enforced, just done by LangChain.
    # --------------------------------

    matches = store.similarity_search_with_score(
        query,
        k=top_k,
        score_threshold=threshold,
    )

    results = [
        {
            "chunks": document.page_content,
            "score": float(score),
        }
        for document, score in matches
    ]

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