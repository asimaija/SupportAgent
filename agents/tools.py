from langchain_core.tools import tool

from rag.retriever import retrieve

from data.complaints import (
    register_complaint,
    get_customer_complaints
)


# =========================================================
# CUSTOMER CONTEXT
# =========================================================

# These values are supplied by app.py before the agent runs.
# The LLM should NOT invent customer identity information.

_current_customer = {
    "name": "",
    "email": "",
    "user_id": ""
}


def set_customer_context(
    name,
    email,
    user_id
):
    """
    Set the currently authenticated customer's information.

    This is called by app.py.
    """

    _current_customer["name"] = name
    _current_customer["email"] = email
    _current_customer["user_id"] = user_id


# =========================================================
# TOOL 1 — COMPANY KNOWLEDGE / RAG
# =========================================================

@tool
def search_company_knowledge(question: str) -> str:
    """
    Search AppInSnap company knowledge using the
    existing Qdrant RAG system.

    Use this for:
    - company information
    - services
    - FAQs
    - policies
    - other AppInSnap information
    """

    results = retrieve(
        question,
        top_k=2,
        threshold=0.35
    )

    if not results:
        return (
            "No relevant information was found "
            "in the AppInSnap knowledge base."
        )

    # Handle different possible retriever formats
    context_parts = []

    for result in results:

        if isinstance(result, str):

            context_parts.append(result)

        elif isinstance(result, dict):

            text = (
                result.get("text")
                or result.get("content")
                or result.get("document")
                or ""
            )

            if text:
                context_parts.append(text)

        else:

            text = getattr(
                result,
                "page_content",
                None
            )

            if text:
                context_parts.append(text)

    if not context_parts:

        return (
            "Relevant results were found, "
            "but no readable content was returned."
        )

    return "\n\n".join(context_parts)


# =========================================================
# TOOL 2 — CREATE COMPLAINT
# =========================================================

@tool
def create_complaint(complaint: str) -> str:
    """
    Register a customer complaint in Firebase.

    Use this when the customer wants to report
    a problem or register a complaint.

    Customer identity comes from the authenticated
    application session, not from the LLM.
    """

    complaint = complaint.strip()

    if not complaint:

        return "Complaint details cannot be empty."

    name = _current_customer["name"]
    email = _current_customer["email"]
    user_id = _current_customer["user_id"]

    if not user_id:

        return (
            "The customer is not authenticated. "
            "Please log in before registering a complaint."
        )

    try:

        complaint_id = register_complaint(
            name,
            complaint,
            email,
            user_id
        )

        return (
            "Complaint registered successfully.\n"
            f"Complaint ID: {complaint_id}\n"
            "Status: Pending"
        )

    except Exception as e:

        return (
            "The complaint could not be registered. "
            f"Error: {str(e)}"
        )


# =========================================================
# TOOL 3 — GET CUSTOMER COMPLAINT STATUS
# =========================================================

@tool
def get_customer_complaint_status() -> str:
    """
    Get the authenticated customer's complaints
    and their current statuses from Firebase.

    Use this when the customer asks about
    complaint status.
    """

    user_id = _current_customer["user_id"]

    if not user_id:

        return (
            "The customer is not authenticated. "
            "Please log in first."
        )

    try:

        complaints = get_customer_complaints(
            user_id
        )

    except Exception as e:

        return (
            "Unable to retrieve complaint status. "
            f"Error: {str(e)}"
        )

    if not complaints:

        return (
            "You do not have any registered complaints."
        )

    results = []

    for complaint in complaints:

        complaint_id = complaint.get(
            "complaint_id",
            ""
        )

        complaint_text = complaint.get(
            "complaint",
            ""
        )

        status = complaint.get(
            "status",
            "Pending"
        )

        results.append(
            f"Complaint ID: {complaint_id}\n"
            f"Complaint: {complaint_text}\n"
            f"Status: {status}"
        )

    return "\n\n".join(results)