import re
import requests

from rag.retriever import retrieve

from data.complaints import get_complaint_status


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"


SYSTEM_PROMPT = """
You are a helpful support assistant for AppInSnap.

Answer using ONLY the provided context.

If the answer is not in the context, say:
Sorry, I don't have that information about AppInSnap.

Keep answers short and clear.
"""


def generate_answer(question, context):

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer:
"""

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

    return response.json()["response"].strip()


def get_status(question):

    match = re.search(
        r"CMP-\d+",
        question.upper()
    )

    if not match:
        return None

    complaint_id = match.group()

    result = get_complaint_status(
        complaint_id
    )

    if not result:

        return (
            f"Complaint {complaint_id} "
            "was not found."
        )

    return (
        f"Complaint ID: {result[0]}\n\n"
        f"Name: {result[1]}\n"
        f"Complaint: {result[2]}\n"
        f"Status: {result[3]}\n"
        f"Created: {result[4]}"
    )


def answer_question(question):

    # Check complaint status first
    if "cmp-" in question.lower():

        status = get_status(question)

        if status:
            return status


    # Normal RAG
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

        return generate_answer(
            question,
            context
        )

    except requests.exceptions.ConnectionError:

        return (
            "⚠️ Ollama is not running. "
            "Please run: ollama serve"
        )

    except Exception as e:

        return f"⚠️ Error: {e}"


if __name__ == "__main__":

    question = input(
        "Ask your question: "
    )

    print(
        answer_question(question)
    )