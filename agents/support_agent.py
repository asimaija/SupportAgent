# =========================================================
# agents/support_agent.py
# =========================================================

from langchain_ollama import ChatOllama
from rag.retriever import retrieve


# =========================================================
# OLLAMA / QWEN
# =========================================================

llm = ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0.2,
)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are the AppInSnap customer support assistant.

You answer ONLY questions related to AppInSnap.

Use ONLY the provided AppInSnap knowledge.

Rules:

1. Do not invent information.
2. Do not use your general knowledge.
3. If the context does not contain the answer, say:
   "I could not find this information in the AppInSnap knowledge base."
4. Keep answers clear and concise.
5. You can answer questions about:
   - AppInSnap
   - AppInSnap services
   - AppInSnap policies
   - AppInSnap FAQs
   - AppInSnap company information

Do NOT handle complaint registration here.
Complaint registration is handled separately by app.py.
"""


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(question):

    if not question or not question.strip():

        return "Please enter a question about AppInSnap."

    question = question.strip()

    # -----------------------------------------------------
    # RETRIEVE RAG CONTEXT
    # -----------------------------------------------------

    try:

        results = retrieve(
            question,
            top_k=3,
            threshold=0.35
        )

    except Exception:

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
    # EXTRACT CHUNKS
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
    # PROMPT QWEN
    # -----------------------------------------------------

    prompt = f"""
{SYSTEM_PROMPT}

AppInSnap Knowledge:

{context}

Customer Question:

{question}

Answer the customer using ONLY the AppInSnap Knowledge above.
"""

    # -----------------------------------------------------
    # CALL QWEN THROUGH OLLAMA
    # -----------------------------------------------------

    try:

        response = llm.invoke(prompt)

        return response.content.strip()

    except Exception as e:

        return (
            "Sorry, I was unable to generate an answer "
            f"at this time. Error: {str(e)}"
        )