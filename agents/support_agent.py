import requests

from rag.retriever import retrieve


# =========================================================
# OLLAMA SETTINGS
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are a customer support assistant.

Answer the user's question using ONLY the information provided
in the retrieved context.

RULES:

1. Do not invent information.

2. Do not use information that is not present in the context.

3. Do not repeat the user's question.

4. Answer the question directly and clearly.

5. Keep the answer concise and easy to understand.

6. If the answer contains multiple items, points, features,
   services, steps, or explanations, use Markdown bullet points.

7. Automatically identify important words and phrases from the
   actual retrieved information and answer.

8. Make important words and phrases bold using Markdown:
   **important term**

9. Important terms must be identified dynamically.

10. Do not use a predefined keyword list.

11. Do not hard-code any company names, service names,
    feature names, product names, policies, departments,
    statuses, or technical terms.

12. Do not bold the entire response.

13. Keep normal explanatory text unbolded.

14. Do not invent headings, categories, services, features,
    policies, or other information.

15. Only create bullets when the answer naturally contains
    multiple points.

16. Preserve the meaning of the retrieved information.

17. If the retrieved information is not sufficient to answer
    the question, clearly say that the information is not
    available.

18. Do not mention RAG, retrieval, embeddings, chunks,
    vector databases, prompts, or internal processing.

19. Do not repeat information unnecessarily.

20. Do not use information from your own general knowledge
    when it is not supported by the retrieved context.
"""


# =========================================================
# GENERATE ANSWER WITH OLLAMA
# =========================================================

def generate_with_ollama(question, context):

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"RETRIEVED INFORMATION:\n"
        f"{context}\n\n"
        f"USER QUESTION:\n"
        f"{question}\n\n"
        f"ANSWER:"
    )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9
            }
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "response",
        ""
    ).strip()


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(question):

    # -----------------------------------------------------
    # Validate question
    # -----------------------------------------------------

    if not question or not question.strip():

        return "Please enter a question."


    question = question.strip()


    # -----------------------------------------------------
    # Retrieve relevant information
    # -----------------------------------------------------

    try:

        results = retrieve(
            question,
            top_k=3,
            threshold=0.35
        )

    except Exception as e:

        return (
            f"Unable to search the knowledge base: {e}"
        )


    # -----------------------------------------------------
    # No relevant results
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

        if isinstance(result, dict):

            chunks = result.get(
                "chunks",
                ""
            )

        else:

            chunks = str(result)


        if chunks:

            context_parts.append(
                str(chunks).strip()
            )


    context = "\n\n".join(
        context_parts
    )


    # -----------------------------------------------------
    # Make sure context exists
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


    # -----------------------------------------------------
    # Ollama connection error
    # -----------------------------------------------------

    except requests.exceptions.ConnectionError:

        return (
            "Could not connect to Ollama. "
            "Please make sure Ollama is running."
        )


    # -----------------------------------------------------
    # Ollama timeout
    # -----------------------------------------------------

    except requests.exceptions.Timeout:

        return (
            "The response took too long. "
            "Please try again."
        )


    # -----------------------------------------------------
    # Other request errors
    # -----------------------------------------------------

    except requests.exceptions.RequestException as e:

        return (
            f"Error generating answer: {e}"
        )


    # -----------------------------------------------------
    # Other unexpected errors
    # -----------------------------------------------------

    except Exception as e:

        return (
            f"An unexpected error occurred: {e}"
        )


    # -----------------------------------------------------
    # Empty LLM response
    # -----------------------------------------------------

    if not answer:

        return (
            "Sorry, I don't have enough information "
            "to answer that."
        )


    # -----------------------------------------------------
    # Return final answer
    # -----------------------------------------------------

    return answer