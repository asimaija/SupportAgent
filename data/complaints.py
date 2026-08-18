from data.firebase_db import db
from datetime import datetime
import uuid


# =========================================================
# REGISTER COMPLAINT
# =========================================================

def register_complaint(
    name,
    complaint,
    email=None,
    user_id=None
):

    complaint_id = (
        "CMP-" +
        str(uuid.uuid4())[:8].upper()
    )

    data = {
        "complaint_id": complaint_id,
        "name": name,
        "complaint": complaint,
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }

    if email:

        data["email"] = email

    if user_id:

        data["user_id"] = user_id

    db.collection(
        "complaints"
    ).document(
        complaint_id
    ).set(data)

    return complaint_id


# =========================================================
# GET COMPLAINT
# =========================================================

def get_complaint(
    complaint_id
):

    complaint_id = complaint_id.strip().upper()

    # Try document ID
    doc = (
        db.collection("complaints")
        .document(complaint_id)
        .get()
    )

    if doc.exists:

        data = doc.to_dict()

        data["complaint_id"] = data.get(
            "complaint_id",
            complaint_id
        )

        return data

    # Fallback search
    results = (
        db.collection("complaints")
        .where(
            "complaint_id",
            "==",
            complaint_id
        )
        .limit(1)
        .stream()
    )

    for document in results:

        data = document.to_dict()

        data["complaint_id"] = data.get(
            "complaint_id",
            complaint_id
        )

        return data

    return None


# =========================================================
# GET CUSTOMER COMPLAINTS
# =========================================================

def get_customer_complaints(
    user_id
):

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

        data["complaint_id"] = data.get(
            "complaint_id",
            doc.id
        )

        complaints.append(data)

    return complaints


# =========================================================
# GET ALL COMPLAINTS
# =========================================================

def get_all_complaints():

    complaints = []

    docs = (
        db.collection("complaints")
        .stream()
    )

    for doc in docs:

        data = doc.to_dict()

        data["document_id"] = doc.id

        data["complaint_id"] = data.get(
            "complaint_id",
            doc.id
        )

        data["status"] = data.get(
            "status",
            "Pending"
        )

        complaints.append(data)

    return complaints


# =========================================================
# UPDATE STATUS
# =========================================================

def update_complaint_status(
    complaint_id,
    new_status
):

    complaint_id = complaint_id.strip().upper()

    # Try document ID
    doc_ref = (
        db.collection("complaints")
        .document(complaint_id)
    )

    doc = doc_ref.get()

    if doc.exists:

        doc_ref.update({
            "status": new_status,
            "updated_at": datetime.now().isoformat()
        })

        return True

    # Fallback search
    results = (
        db.collection("complaints")
        .where(
            "complaint_id",
            "==",
            complaint_id
        )
        .limit(1)
        .stream()
    )

    for document in results:

        document.reference.update({
            "status": new_status,
            "updated_at": datetime.now().isoformat()
        })

        return True

    return False