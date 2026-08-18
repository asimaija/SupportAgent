from data.firebase_db import db

print("Firebase connected!")

ref = db.collection("complaints").document("TEST-CMP")

ref.set({
    "complaint_id": "TEST-CMP",
    "name": "Test User",
    "complaint": "Firebase connection test",
    "status": "Pending"
})

print("Complaint test document created!")