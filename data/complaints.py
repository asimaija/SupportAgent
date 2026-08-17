from data.firebase_db import db
from datetime import datetime
import uuid


def register_complaint(name, complaint):

    complaint_id = "CMP-" + str(uuid.uuid4())[:8].upper()

    data = {
        "complaint_id": complaint_id,
        "name": name,
        "complaint": complaint,
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }

    db.collection("complaints").document(complaint_id).set(data)

    return complaint_id


def get_complaint(complaint_id):

    doc = db.collection("complaints").document(complaint_id).get()

    if doc.exists:
        return doc.to_dict()

    return None


def get_all_complaints():

    complaints = []

    for doc in db.collection("complaints").stream():

        data = doc.to_dict()

        # Use document ID if complaint_id field is missing
        data["complaint_id"] = data.get(
            "complaint_id",
            doc.id
        )

        # Default status
        data["status"] = data.get(
            "status",
            "Pending"
        )

        complaints.append(data)

    return complaints


def update_complaint_status(complaint_id, status):

    db.collection("complaints").document(
        complaint_id
    ).update({
        "status": status
    })