# =========================================================
# data/complaints.py
# =========================================================

from datetime import datetime
import uuid

from data.firebase_db import db


# =========================================================
# REGISTER COMPLAINT
# =========================================================

def register_complaint(
    name,
    complaint,
    email,
    user_id,
    category=None,
    department=None
):
    """
    Register a customer complaint in Firebase Firestore.

    category / department come from
    agents/complaint_classifier.classify_complaint() — passed in here
    rather than computed inside this function, so this module stays
    a pure data-access layer (Firestore in, Firestore out) and
    doesn't need to know classification exists.

    Returns:
        Complaint ID
    """

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not user_id:
        raise ValueError(
            "Customer user ID is required."
        )

    if not complaint or not complaint.strip():
        raise ValueError(
            "Complaint details cannot be empty."
        )

    # -----------------------------------------------------
    # CREATE COMPLAINT ID
    # -----------------------------------------------------

    complaint_id = (
        "CMP-"
        + str(uuid.uuid4())[:8].upper()
    )

    # -----------------------------------------------------
    # CREATE DATA
    # -----------------------------------------------------

    data = {

        "complaint_id": complaint_id,

        "name": (
            name.strip()
            if name
            else ""
        ),

        "email": (
            email.strip()
            if email
            else ""
        ),

        "user_id": user_id,

        "complaint": complaint.strip(),

        "category": category or "General",

        "department": department or "General Support",

        "status": "Pending",

        "created_at": datetime.now().isoformat()
    }

    # -----------------------------------------------------
    # SAVE TO FIRESTORE
    # -----------------------------------------------------

    db.collection(
        "complaints"
    ).document(
        complaint_id
    ).set(data)

    # -----------------------------------------------------
    # RETURN COMPLAINT ID
    # -----------------------------------------------------

    return complaint_id


# =========================================================
# GET CUSTOMER COMPLAINTS
# =========================================================

def get_customer_complaints(user_id):
    """
    Return only complaints belonging to the
    authenticated customer.
    """

    if not user_id:
        return []

    complaints = []

    docs = (
        db.collection("complaints")
        .where(
            "user_id",
            "==",
            user_id
        )
        .stream()
    )

    for doc in docs:

        data = doc.to_dict()

        # Safety fallback
        if not data.get("complaint_id"):
            data["complaint_id"] = doc.id

        if not data.get("status"):
            data["status"] = "Pending"

        if not data.get("category"):
            data["category"] = "General"

        if not data.get("department"):
            data["department"] = "General Support"

        complaints.append(data)

    # -----------------------------------------------------
    # NEWEST FIRST
    # -----------------------------------------------------

    complaints.sort(
        key=lambda x: x.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return complaints


# =========================================================
# GET SINGLE COMPLAINT
# =========================================================

def get_complaint(complaint_id):
    """
    Get one complaint by Complaint ID.
    """

    if not complaint_id:
        return None

    doc = (
        db.collection("complaints")
        .document(complaint_id)
        .get()
    )

    if not doc.exists:
        return None

    data = doc.to_dict()

    if not data.get("complaint_id"):
        data["complaint_id"] = doc.id

    if not data.get("status"):
        data["status"] = "Pending"

    if not data.get("category"):
        data["category"] = "General"

    if not data.get("department"):
        data["department"] = "General Support"

    return data


# =========================================================
# UPDATE COMPLAINT STATUS
# =========================================================

def update_complaint_status(
    complaint_id,
    status
):
    """
    Update the status of a complaint.

    Allowed statuses:
        Pending
        In Progress
        Resolved
    """

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_statuses:
        raise ValueError(
            "Invalid complaint status."
        )

    if not complaint_id:
        raise ValueError(
            "Complaint ID is required."
        )

    # -----------------------------------------------------
    # FIND COMPLAINT
    # -----------------------------------------------------

    doc_ref = (
        db.collection("complaints")
        .document(complaint_id)
    )

    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError(
            "Complaint not found."
        )

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    doc_ref.update({

        "status": status,

        "updated_at": (
            datetime.now().isoformat()
        )
    })

    return True


# =========================================================
# GET ALL COMPLAINTS
# =========================================================

def get_all_complaints():
    """
    Get all complaints.

    Used by the admin dashboard.
    """

    complaints = []

    docs = (
        db.collection("complaints")
        .stream()
    )

    for doc in docs:

        data = doc.to_dict()

        if not data.get("complaint_id"):
            data["complaint_id"] = doc.id

        if not data.get("status"):
            data["status"] = "Pending"

        if not data.get("category"):
            data["category"] = "General"

        if not data.get("department"):
            data["department"] = "General Support"

        complaints.append(data)

    # -----------------------------------------------------
    # NEWEST FIRST
    # -----------------------------------------------------

    complaints.sort(
        key=lambda x: x.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return complaints