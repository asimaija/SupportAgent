from data.firebase_db import db


def is_admin(user_id):

    if not user_id:
        return False

    try:

        # Find the Firebase Authentication user
        # inside the Firestore users collection.
        doc = (
            db.collection("users")
            .document(user_id)
            .get()
        )

        # User document does not exist.
        if not doc.exists:
            return False

        # Read Firestore fields.
        data = doc.to_dict()

        # User must have role = admin.
        return data.get("role") == "admin"

    except Exception:
        return False