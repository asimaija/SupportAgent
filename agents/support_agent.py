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
GROQ_MODEL = get_groq_model() or "openai/gpt-oss-120b"
NO_MATCH = "NO_MATCH"




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
5. Format every answer the same way:
   - Start with a short 2-line description that directly answers
     the question, in plain sentences.
   - Follow it with exactly 3 bullet points ("- ") that each add a
     concrete detail, step, or example.
   - Wrap the most important word or phrase in each line in
     **double asterisks** (markdown bold) — e.g. the feature name,
     a key setting, a limit, a deadline. Bold only what matters;
     do not bold entire sentences.
   - Do not use headings, backticks, or numbered lists — just the
     2-line intro plus the 3 bullets described above.
6. Never handle complaint registration here — that is handled
   separately by app.py.
"""


# =========================================================
# Clean up a model's answer without touching intentional **bold**.
#
# Rule 5 above asks for bold on key words plus a 2-line-intro +
# 3-bullets shape. Small/fast models sometimes still slip in a
# heading or a stray backtick, so this strips just those — bold
# markers are left alone since the UI renders them.
# =========================================================

import re

_HEADING_RE = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def _clean_answer_formatting(text):

    if not text:
        return text

    text = _HEADING_RE.sub("", text)
    text = _INLINE_CODE_RE.sub(r"\1", text)

    return text.strip()


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
            return _clean_answer_formatting(final.content)
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
        return _clean_answer_formatting(final.content)
    except Exception as e:
        return f"Sorry, I was unable to generate an answer. Error: {e}"