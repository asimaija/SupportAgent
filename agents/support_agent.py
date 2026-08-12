from rag.retriever import retrieve
import ollama


def answer_question(question):

    results = retrieve(
        question,
        top_k=3,
        threshold=0.45
    )

    # No relevant AppInSnap information
    if not results:

        return (
            "Sorry, I can only answer questions "
            "related to AppInSnap."
        )


    # Create context
    context = ""

    for result in results:

        context += result["chunks"]
        context += "\n\n"


    prompt = f"""
You are an AppInSnap customer support assistant.

IMPORTANT RULES:

1. Answer ONLY using the CONTEXT below.
2. Do NOT use your own knowledge.
3. Do NOT answer general knowledge questions.
4. Do NOT invent information.
5. If the context does not contain the answer, say:
   "Sorry, I don't have that information about AppInSnap."

CONTEXT:
{context}

CUSTOMER QUESTION:
{question}

ANSWER:
"""


    response = ollama.chat(

        model="qwen2.5:0.5b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response["message"]["content"]


if __name__ == "__main__":

    question = input("Ask your question: ")

    answer = answer_question(question)

    print("\n# Answer:\n")
    print(answer)