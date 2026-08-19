import streamlit as st
import requests


# =========================================================
# FIREBASE AUTH SETTINGS
# =========================================================

def get_api_key():

    try:
        api_key = st.secrets["FIREBASE_API_KEY"]

        if not api_key:
            return None

        return api_key.strip()

    except Exception:
        return None


# =========================================================
# FORMAT FIREBASE ERROR
# =========================================================

def firebase_error(response):

    try:

        data = response.json()

        message = (
            data
            .get("error", {})
            .get("message", "Authentication failed.")
        )

    except Exception:

        return "Authentication service error."

    errors = {

        "EMAIL_EXISTS":
            "This email is already registered.",

        "INVALID_EMAIL":
            "Please enter a valid email address.",

        "WEAK_PASSWORD":
            "Password must be at least 6 characters.",

        "OPERATION_NOT_ALLOWED":
            "Email/Password authentication is not enabled in Firebase.",

        "CONFIGURATION_NOT_FOUND":
            "Firebase Authentication is not configured correctly. "
            "Please enable Email/Password authentication in Firebase Console.",

        "INVALID_PASSWORD":
            "Incorrect password.",

        "EMAIL_NOT_FOUND":
            "No account exists with this email.",

        "USER_DISABLED":
            "This account has been disabled.",

        "TOO_MANY_ATTEMPTS_TRY_LATER":
            "Too many attempts. Please try again later."
    }

    return errors.get(
        message,
        message
    )


# =========================================================
# FIREBASE AUTHENTICATION LOGIN
# =========================================================

def login_firebase_user(
    email,
    password
):

    api_key = get_api_key()

    if not api_key:

        return {
            "success": False,
            "error": (
                "FIREBASE_API_KEY is missing from "
                ".streamlit/secrets.toml"
            )
        }

    url = (
        "https://identitytoolkit.googleapis.com/"
        "v1/accounts:signInWithPassword"
        f"?key={api_key}"
    )

    payload = {
        "email": email.strip(),
        "password": password,
        "returnSecureToken": True
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:

            return {
                "success": False,
                "error": firebase_error(response)
            }

        data = response.json()

        return {
            "success": True,
            "localId": data.get("localId"),
            "email": data.get("email"),
            "idToken": data.get("idToken"),
            "refreshToken": data.get("refreshToken")
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "error": f"Firebase connection error: {e}"
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# =========================================================
# CUSTOMER REGISTER
# =========================================================

def register_customer(
    name,
    email,
    password
):

    api_key = get_api_key()

    if not api_key:

        return {
            "success": False,
            "error": (
                "FIREBASE_API_KEY is missing from "
                ".streamlit/secrets.toml"
            )
        }

    url = (
        "https://identitytoolkit.googleapis.com/"
        "v1/accounts:signUp"
        f"?key={api_key}"
    )

    payload = {
        "email": email.strip(),
        "password": password,
        "returnSecureToken": True
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:

            return {
                "success": False,
                "error": firebase_error(response)
            }

        data = response.json()

        return {
            "success": True,
            "localId": data.get("localId"),
            "email": data.get("email"),
            "idToken": data.get("idToken"),
            "refreshToken": data.get("refreshToken")
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "error": f"Firebase connection error: {e}"
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# =========================================================
# CUSTOMER LOGIN
# =========================================================

def login_customer(
    email,
    password
):

    return login_firebase_user(
        email,
        password
    )