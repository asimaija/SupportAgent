import requests

from rag.retriever import retrieve


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"


SYSTEM_PROMPT = (
    "You are a helpful support assistant for AppInSnap. "
    "Answer the user's question using ONLY the context provided below. "
    "If the context does not contain the answer, say you don't have "
    "that information about AppInSnap. Keep answers concise and clear."
)


def generate_with_ollama(question, context):

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", "").strip()


def answer_question(question):

    # --------------------------------
    # Retrieve relevant information by
    # comparing question embedding to
    # stored chunk embeddings
    # --------------------------------

    results = retrieve(
        question,
        top_k=3,
        threshold=0.35
    )

    if not results:
        return (
            "Sorry, I don't have that information "
            "about AppInSnap."
        )

    # --------------------------------
    # Combine retrieved chunks into
    # context for the LLM
    # --------------------------------

    context = "\n\n".join(
        result["chunks"] for result in results
    )

    # --------------------------------
    # Ask the local LLM (Ollama) to
    # generate a grounded answer
    # --------------------------------

    try:
        answer = generate_with_ollama(question, context)

    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Could not connect to Ollama. Make sure it's running "
            "(try: `ollama serve`) and that the model "
            f"'{OLLAMA_MODEL}' is available."
        )

    except requests.exceptions.RequestException as e:
        return f"⚠️ Error generating answer: {e}"

    if not answer:
        return (
            "Sorry, I don't have that information "
            "about AppInSnap."
        )

    return answer.strip()


if __name__ == "__main__":

    question = input("Ask your question: ")

    answer = answer_question(question)

    print("\n# Answer:\n")
    print(answer)