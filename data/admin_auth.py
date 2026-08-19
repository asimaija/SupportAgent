from data.firebase_db import db


def is_admin(user_id):

    if not user_id:
        return False

    try:

        doc = (
            db.collection("admins")
            .document(user_id)
            .get()
        )

        if not doc.exists:
            return False

        data = doc.to_dict()

        return (
            data.get("role") == "admin"
            and data.get("active", True) is True
        )

    except Exception:

        return False