import streamlit as st
import requests


# =========================================================
# FIREBASE AUTH SETTINGS
# =========================================================

def get_api_key():

    try:
        return st.secrets["FIREBASE_API_KEY"]

    except Exception:

        return None


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
            "error": "FIREBASE_API_KEY is missing."
        }

    url = (
        "https://identitytoolkit.googleapis.com/"
        "v1/accounts:signUp?key="
        + api_key
    )

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:

        response = requests.post(
            url,
            json=payload
        )

        data = response.json()

        if response.status_code != 200:

            return {
                "success": False,
                "error": data.get(
                    "error",
                    {}
                ).get(
                    "message",
                    "Registration failed."
                )
            }

        return {
            "success": True,
            "localId": data.get("localId"),
            "email": data.get("email"),
            "idToken": data.get("idToken")
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

    api_key = get_api_key()

    if not api_key:

        return {
            "success": False,
            "error": "FIREBASE_API_KEY is missing."
        }

    url = (
        "https://identitytoolkit.googleapis.com/"
        "v1/accounts:signInWithPassword?key="
        + api_key
    )

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:

        response = requests.post(
            url,
            json=payload
        )

        data = response.json()

        if response.status_code != 200:

            return {
                "success": False,
                "error": data.get(
                    "error",
                    {}
                ).get(
                    "message",
                    "Login failed."
                )
            }

        return {
            "success": True,
            "localId": data.get("localId"),
            "email": data.get("email"),
            "idToken": data.get("idToken")
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }