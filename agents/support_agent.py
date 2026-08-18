import requests

from rag.retriever import retrieve


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"


SYSTEM_PROMPT = """
You are the AppInSnap customer support assistant.

Answer the user's question using the provided knowledge.

IMPORTANT RESPONSE FORMAT:

1. Start with exactly ONE short sentence that directly answers
   the user's question.

2. If the answer contains multiple items, features, services,
   steps, or points, present them as bullet points.

3. Automatically identify important words, names, services,
   features, policies, statuses, and technical terms and make
   those important terms bold using Markdown.

4. Do NOT use a hard-coded list of words.
   Decide which terms are important based on the question
   and the provided information.

5. Keep normal explanatory text unbolded.

6. Keep the response concise and easy to read.

7. Do not repeat the user's question.

8. Do not invent information.

Example format:

**AppInSnap** provides several services for businesses.

- **UI/UX Design** — Creates user-friendly interfaces.
- **Web Development** — Builds modern web applications.
- **Data Science** — Provides data-driven solutions.

The important terms above are examples only.
Do not treat them as a fixed list.
"""

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

    return response.json().get(
        "response",
        ""
    ).strip()


def answer_question(question):

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

    context = "\n\n".join(
        result["chunks"]
        for result in results
    )

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

    except requests.exceptions.RequestException as e:

        return f"Error generating answer: {e}"

    if not answer:

        return (
            "Sorry, I don't have that information "
            "about AppInSnap."
        )

    return answer