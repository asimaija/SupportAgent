import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "firebase_config.json"


if not firebase_admin._apps:

    cred = credentials.Certificate(
        str(CREDENTIALS_FILE)
    )

    firebase_admin.initialize_app(cred)


db = firestore.client()