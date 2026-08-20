# =========================================================
# agents/support_agent.py
#
# The support agent is a small LangChain "tool-calling" agent:
#
#   - The LLM (served by Groq) is given exactly ONE tool:
#     `search_appinsnap_knowledge`, which searches the AppInSnap
#     knowledge base (rag/retriever.py -> Qdrant).
#
#   - The model is instructed to ALWAYS call that tool before
#     answering, and to answer using nothing but what the tool
#     returns.
#
#   - If the tool finds nothing relevant (i.e. the question isn't
#     about AppInSnap, or the answer just isn't in the knowledge
#     base), the fixed refusal message is returned directly — this
#     does NOT depend on the model "choosing" to be honest, it's
#     enforced in code, so scope stays tight even with a small /
#     cheap model.
# =========================================================

import os

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
)

from rag.retriever import retrieve


# =========================================================
# WHAT LANGCHAIN IS DOING HERE (short version)
# =========================================================
# LangChain is just the glue: it gives every LLM provider (Groq,
# OpenAI, Ollama, ...) the same `ChatModel` interface, and gives
# "tools" (plain Python functions) a standard schema the model can
# call. Swapping Ollama for Groq below only required changing this
# one import + constructor — none of app.py, the RAG pipeline, or
# the complaint flow had to change. That decoupling (one interface
# for models, tools, and prompts) is the whole value of LangChain.
# =========================================================


# =========================================================
# GROQ API KEY
#
# Checked in this order:
#   1. .streamlit/secrets.toml   -> GROQ_API_KEY   (same pattern
#      already used for FIREBASE_API_KEY in customer/auth.py)
#   2. Environment variable      -> GROQ_API_KEY
# =========================================================

def get_groq_api_key():

    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            return key.strip()
    except Exception:
        pass

    return os.environ.get("GROQ_API_KEY")


def get_groq_model():

    try:
        if "GROQ_MODEL" in st.secrets and st.secrets["GROQ_MODEL"]:
            return st.secrets["GROQ_MODEL"].strip()
    except Exception:
        pass

    return os.environ.get("GROQ_MODEL")


GROQ_API_KEY = get_groq_api_key()

# Groq deprecated the llama-3.x models in June 2026. This is their
# recommended replacement for llama-3.3-70b-versatile: strong quality,
# fast inference. Override with GROQ_MODEL (env var or secret) if you
# want something else — e.g. "openai/gpt-oss-20b" for lower latency,
# or "qwen/qwen3.6-27b" for their current highest-intelligence model.
GROQ_MODEL = get_groq_model() or "openai/gpt-oss-120b"


NO_MATCH = "NO_MATCH"


# =========================================================
# TOOL: search the AppInSnap knowledge base
# =========================================================

@tool
def search_appinsnap_knowledge(query: str) -> str:
    """
    Search the AppInSnap knowledge base for information relevant to
    the customer's question. Always call this before answering any
    customer question. Returns the most relevant knowledge-base
    passages, or the literal string "NO_MATCH" if nothing relevant
    was found (in which case AppInSnap has no information on this
    topic and you must say so — do not use outside knowledge).
    """

    try:
        results = retrieve(query, top_k=3, threshold=0.45)
    except Exception:
        return NO_MATCH

    chunks = []

    for result in results:

        if isinstance(result, dict):
            text = (
                result.get("chunks")
                or result.get("text")
                or result.get("content")
                or ""
            )
        else:
            text = getattr(result, "page_content", "")

        if text and text.strip():
            chunks.append(text.strip())

    if not chunks:
        return NO_MATCH

    return "\n\n---\n\n".join(chunks)


TOOLS = [search_appinsnap_knowledge]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are the AppInSnap customer support assistant.

You answer ONLY questions related to AppInSnap (the app, its
features, services, policies, account/billing, or usage).

You have one tool available: search_appinsnap_knowledge.

Rules:

1. For every customer question, call search_appinsnap_knowledge
   first. Never answer from memory before searching.
2. Answer using ONLY the text the tool returns. Do not invent
   information and do not fall back on your own general knowledge.
3. If the tool returns "NO_MATCH", or the question is unrelated to
   AppInSnap, reply with exactly:
   "I could not find this information in the AppInSnap knowledge base."
4. Keep answers clear, concise, and in a helpful support-agent tone.
5. Never handle complaint registration here — that is handled
   separately by app.py.
"""


# =========================================================
# BUILD THE MODEL (lazy, so a missing API key doesn't crash imports)
# =========================================================

_llm = None
_llm_with_tools = None


def _get_llm():

    global _llm, _llm_with_tools

    if _llm is None:

        _llm = ChatGroq(
            model=GROQ_MODEL,
            temperature=0.2,
            api_key=GROQ_API_KEY,
        )

        _llm_with_tools = _llm.bind_tools(TOOLS)

    return _llm_with_tools


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(question):

    if not question or not question.strip():
        return "Please enter a question about AppInSnap."

    question = question.strip()

    if not GROQ_API_KEY:
        return (
            "Groq is not configured. Add GROQ_API_KEY to "
            ".streamlit/secrets.toml (or as an environment "
            "variable) to enable the support assistant."
        )

    try:
        llm_with_tools = _get_llm()
    except Exception as e:
        return f"Sorry, I was unable to start the assistant. Error: {e}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    # -----------------------------------------------------
    # 1st call — the model should call search_appinsnap_knowledge
    # -----------------------------------------------------

    try:
        ai_message = llm_with_tools.invoke(messages)
    except Exception as e:
        return f"Sorry, I was unable to generate an answer. Error: {e}"

    tool_calls = getattr(ai_message, "tool_calls", None) or []

    # -----------------------------------------------------
    # Safety net: if the model skipped the tool (small/cheap
    # models occasionally do), search ourselves so the answer
    # still stays grounded in the knowledge base.
    # -----------------------------------------------------

    if not tool_calls:

        tool_result = search_appinsnap_knowledge.invoke(
            {"query": question}
        )

        if tool_result == NO_MATCH:
            return "I could not find this information in the AppInSnap knowledge base."

        messages.append(ai_message)
        messages.append(
            ToolMessage(
                content=tool_result,
                tool_call_id="fallback_search",
            )
        )

        try:
            final = llm_with_tools.invoke(messages)
            return final.content.strip()
        except Exception as e:
            return f"Sorry, I was unable to generate an answer. Error: {e}"

    # -----------------------------------------------------
    # Normal path — execute every tool call the model requested
    # -----------------------------------------------------

    messages.append(ai_message)

    any_match = False

    for call in tool_calls:

        tool_fn = TOOLS_BY_NAME.get(call["name"])

        if tool_fn is None:
            result = NO_MATCH
        else:
            result = tool_fn.invoke(call["args"])

        if result != NO_MATCH:
            any_match = True

        messages.append(
            ToolMessage(
                content=result,
                tool_call_id=call["id"],
            )
        )

    # Enforced in code, not left to the model: if nothing relevant
    # was found in the knowledge base, refuse immediately.
    if not any_match:
        return "I could not find this information in the AppInSnap knowledge base."

    # -----------------------------------------------------
    # 2nd call — model writes the final answer from tool output
    # -----------------------------------------------------

    try:
        final = llm_with_tools.invoke(messages)
        return final.content.strip()
    except Exception as e:
        return f"Sorry, I was unable to generate an answer. Error: {e}"