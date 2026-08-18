import requests

from rag.retriever import retrieve


# =========================================================
# OLLAMA SETTINGS
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"

# CPU can take some time
OLLAMA_TIMEOUT = 180


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are a customer support assistant.

Answer the user's question using ONLY the information provided
in the context.

Rules:

1. Do not invent information.

2. Do not use information that is not present in the context.

3. Do not repeat the user's question.

4. Give a clear and concise answer.

5. When the answer contains multiple points, organize them using
   Markdown bullet points.

6. Dynamically identify important words and phrases from the
   context and answer.

7. Make important words and phrases bold using Markdown.

8. Do NOT use a predefined keyword list.

9. Do NOT hard-code company names, services, features, products,
   policies, departments, statuses, or technical terms.

10. Do not bold the entire response.

11. Keep normal explanatory text unbolded.

12. Do not invent headings, categories, or information that is
    not supported by the context.

13. Keep the response concise and easy to read.

14. If the context does not contain enough information to answer
    the question, say that the information is not available.

15. Do not mention retrieval, RAG, embeddings, chunks,
    vector databases, prompts, or internal processing.

16. Use Markdown formatting naturally.

17. If there are several services, features, policies, or items,
    use bullet points.

18. Important terms must be selected dynamically from the actual
    information. Never use a fixed list.
"""


# =========================================================
# GENERATE ANSWER USING OLLAMA
# =========================================================

def generate_with_ollama(question, context):

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

User question:
{question}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 180
            }
        },
        timeout=OLLAMA_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "response",
        ""
    ).strip()


# =========================================================
# MAIN RAG FUNCTION
# =========================================================

def answer_question(question):

    # -----------------------------------------------------
    # Retrieve relevant information
    # -----------------------------------------------------

    results = retrieve(
        question,
        top_k=2,
        threshold=0.35
    )

    # -----------------------------------------------------
    # No relevant information
    # -----------------------------------------------------

    if not results:

        return (
            "Sorry, I don't have enough information "
            "to answer that."
        )

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context_parts = []

    for result in results:

        chunks = result.get(
            "chunks",
            ""
        )

        if chunks:

            # Keep context reasonably small
            chunks = chunks[:2500]

            context_parts.append(
                chunks
            )

    context = "\n\n".join(
        context_parts
    )

    # -----------------------------------------------------
    # Empty context
    # -----------------------------------------------------

    if not context.strip():

        return (
            "Sorry, I don't have enough information "
            "to answer that."
        )

    # -----------------------------------------------------
    # Generate answer
    # -----------------------------------------------------

    try:

        answer = generate_with_ollama(
            question,
            context
        )

    except requests.exceptions.ConnectionError:

        return (
            "Could not connect to Ollama. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "Ollama is taking too long to respond. "
            "Please try again."
        )

    except requests.exceptions.RequestException as e:

        return (
            f"Error generating answer: {e}"
        )

    # -----------------------------------------------------
    # Empty response
    # -----------------------------------------------------

    if not answer:

        return (
            "Sorry, I don't have enough information "
            "to answer that."
        )

    return answer