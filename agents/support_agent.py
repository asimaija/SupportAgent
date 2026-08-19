# =========================================================
# agents/support_agent.py
# =========================================================

from rag.retriever import retrieve


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(question):
    """
    Answer normal AppInSnap questions using the RAG system.

    Complaint registration is NOT handled here.
    Complaint detection and registration are handled
    separately by app.py.
    """

    if not question or not question.strip():

        return (
            "Please enter a question about AppInSnap."
        )

    question = question.strip()

    # -----------------------------------------------------
    # RETRIEVE COMPANY KNOWLEDGE
    # -----------------------------------------------------

    try:

        results = retrieve(
            question,
            top_k=3,
            threshold=0.35
        )

    except Exception as e:

        return (
            "Sorry, I was unable to search the "
            "AppInSnap knowledge base."
        )

    # -----------------------------------------------------
    # NO RESULTS
    # -----------------------------------------------------

    if not results:

        return (
            "I could not find relevant information "
            "about AppInSnap in my knowledge base."
        )

    # -----------------------------------------------------
    # EXTRACT TEXT
    # -----------------------------------------------------

    context_parts = []

    for result in results:

        if isinstance(result, dict):

            text = (
                result.get("chunks")
                or result.get("text")
                or result.get("content")
                or ""
            )

            if text.strip():

                context_parts.append(
                    text.strip()
                )

        else:

            text = getattr(
                result,
                "page_content",
                ""
            )

            if text and text.strip():

                context_parts.append(
                    text.strip()
                )

    # -----------------------------------------------------
    # NO READABLE CONTENT
    # -----------------------------------------------------

    if not context_parts:

        return (
            "I found relevant AppInSnap information, "
            "but I could not read the retrieved content."
        )

    # -----------------------------------------------------
    # BUILD CONTEXT
    # -----------------------------------------------------

    context = "\n\n---\n\n".join(
        context_parts
    )

    # -----------------------------------------------------
    # RETURN RAG INFORMATION
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # We are not using an LLM here.
    #
    # This prevents Qwen 0.5B from inventing answers
    # or answering unrelated questions.
    #
    # The retrieved AppInSnap information is returned
    # directly.
    # -----------------------------------------------------

    return context