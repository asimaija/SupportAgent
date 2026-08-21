# =========================================================
# agents/complaint_classifier.py
#
# The "Classify Complaint" + "Select Department" steps from the
# architecture diagram. Once agents/complaint_detector.py has already
# decided a message IS a complaint, and the customer has typed out
# the details, this module decides WHAT KIND of complaint it is and
# which team should own it.
#
# Now backed by the same Groq LLM (via LangChain) used by
# agents/support_agent.py, so classification can generalize beyond
# fixed keyword lists. The original regex rules are kept as a
# fallback — used automatically if GROQ_API_KEY isn't configured or
# the LLM call fails for any reason — so registering a complaint
# never breaks just because classification did.
# =========================================================

import os
import re

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage


# =========================================================
# CATEGORIES
# =========================================================

CATEGORY_DEPARTMENTS = {
    "Billing": "Billing & Payments",
    "Account": "Account Support",
    "Technical": "Engineering",
    "Service": "Customer Service",
    "General": "General Support",
}

DEFAULT_CATEGORY = "General"
DEFAULT_DEPARTMENT = "General Support"


# =========================================================
# REGEX FALLBACK — same rules as before, only used when the LLM
# path is unavailable or fails.
# =========================================================

# Ordered — first matching category wins, so put more specific
# categories (Billing, Account) before the catch-all Technical/Service
# patterns that might otherwise shadow them.
CATEGORY_RULES = [

    (
        "Billing",
        [
            r"\bcharged twice\b",
            r"\bdouble charged\b",
            r"\bwrong charge\b",
            r"\bovercharged\b",
            r"\bpayment failed\b",
            r"\bpayment issue\b",
            r"\brefund\b",
            r"\bbilling\b",
            r"\binvoice\b",
            r"\bsubscription\b",
        ],
    ),

    (
        "Account",
        [
            r"\bcannot login\b",
            r"\bcan't login\b",
            r"\bcannot log in\b",
            r"\bcan't log in\b",
            r"\blocked out\b",
            r"\bpassword\b",
            r"\baccount\b",
            r"\bverification\b",
            r"\botp\b",
        ],
    ),

    (
        "Technical",
        [
            r"\bbug\b",
            r"\bcrash",
            r"\berror\b",
            r"\bexception\b",
            r"\bnot working\b",
            r"\bdoesn't work\b",
            r"\bdoes not work\b",
            r"\bwon't work\b",
            r"\bfroze\b",
            r"\bfreezing\b",
            r"\bslow\b",
        ],
    ),

    (
        "Service",
        [
            r"\bnot receiving\b",
            r"\bnot received\b",
            r"\bmissing\b",
            r"\bdelayed\b",
            r"\blate\b",
            r"\bnever arrived\b",
        ],
    ),

]


def _rule_based_classify(text):

    text = text.lower().strip()

    for category, patterns in CATEGORY_RULES:

        for pattern in patterns:

            if re.search(pattern, text):

                return category, CATEGORY_DEPARTMENTS[category]

    return DEFAULT_CATEGORY, DEFAULT_DEPARTMENT


# =========================================================
# LLM PATH (LangChain + Groq) — same credentials/model lookup as
# agents/support_agent.py, kept independent here so this module
# doesn't depend on that one importing successfully.
# =========================================================

def _get_groq_api_key():

    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            return key.strip()
    except Exception:
        pass

    return os.environ.get("GROQ_API_KEY")


def _get_groq_model():

    try:
        if "GROQ_MODEL" in st.secrets and st.secrets["GROQ_MODEL"]:
            return st.secrets["GROQ_MODEL"].strip()
    except Exception:
        pass

    return os.environ.get("GROQ_MODEL")


GROQ_API_KEY = _get_groq_api_key()
GROQ_MODEL = _get_groq_model() or "openai/gpt-oss-120b"

_ALLOWED_CATEGORIES = list(CATEGORY_DEPARTMENTS.keys())

CLASSIFIER_SYSTEM_PROMPT = f"""
You are a complaint triage classifier for AppInSnap customer support.

Read the customer's complaint and choose exactly ONE category from
this fixed list: {", ".join(_ALLOWED_CATEGORIES)}.

Guidance:
- Billing: payments, charges, refunds, invoices, subscriptions.
- Account: login, password, verification, being locked out.
- Technical: bugs, crashes, errors, app not working, performance.
- Service: missing, delayed, or never-arrived orders/services.
- General: anything that doesn't clearly fit the above.

Reply with ONLY the single category word from the list above —
no punctuation, no explanation, nothing else.
"""

_llm = None


def _get_llm():

    global _llm

    if _llm is None:

        _llm = ChatGroq(
            model=GROQ_MODEL,
            temperature=0,
            api_key=GROQ_API_KEY,
        )

    return _llm


def _llm_classify(text):
    """
    Returns (category, department) from the LLM, or None if the
    call fails / isn't configured / returns something unrecognized —
    in every one of those cases the caller falls back to regex.
    """

    if not GROQ_API_KEY:
        return None

    try:

        llm = _get_llm()

        messages = [
            SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
            HumanMessage(content=text.strip()),
        ]

        response = llm.invoke(messages)

        raw = (response.content or "").strip()

        # Be lenient about exact formatting — take the first word
        # and match it case-insensitively against the allowed list.
        first_word = raw.split()[0].strip(".,:;\"'") if raw else ""

        for category in _ALLOWED_CATEGORIES:

            if first_word.lower() == category.lower():

                return category, CATEGORY_DEPARTMENTS[category]

    except Exception:

        pass

    return None


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def classify_complaint(text):
    """
    Classify a complaint's free-text description into a
    (category, department) pair.

    Tries the LLM (LangChain + Groq) first; falls back to the
    regex rules above if the LLM isn't configured, errors out, or
    returns something outside the known categories. Falls back to
    ("General", "General Support") if nothing matches at all —
    every complaint still gets routed somewhere.
    """

    if not text or not text.strip():
        return DEFAULT_CATEGORY, DEFAULT_DEPARTMENT

    llm_result = _llm_classify(text)

    if llm_result is not None:
        return llm_result

    return _rule_based_classify(text)