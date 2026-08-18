import streamlit as st

from agents.support_agent import answer_question
from agents.complaint_detector import is_complaint

from data.complaints import (
    register_complaint,
    get_complaint,
    get_customer_complaints
)

from customer.auth import (
    register_customer,
    login_customer
)

from admin.admin_dashboard import admin_dashboard


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AppInSnap Support",
    page_icon="⚡",
    layout="centered"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 850px;
        padding-top: 25px;
    }

    div.stButton > button {
        background-color: #3B4CE0;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #2E3BBE;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    "customer_logged_in": False,

    "customer_name": "",

    "customer_email": "",

    "customer_user_id": "",

    "id_token": "",

    "messages": [],

    "waiting_for_name": False,

    "waiting_for_complaint": False,

    "admin_logged_in": False,

    "admin_complaint": None
}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# HEADER
# =========================================================

st.title("AppInSnap Support")


# =========================================================
# CUSTOMER NOT LOGGED IN
# =========================================================

if not st.session_state.customer_logged_in:

    st.sidebar.image(
        "images/logo.png",
        width=130
    )

    st.sidebar.markdown("---")

    account_page = st.sidebar.radio(
        "Customer Account",
        [
            "Login",
            "Register",
            "Staff / Admin"
        ]
    )

    # =====================================================
    # CUSTOMER REGISTER
    # =====================================================

    if account_page == "Register":

        st.header(
            "Create Customer Account"
        )

        st.caption(
            "Register before using AppInSnap Support."
        )

        with st.form(
            "customer_register"
        ):

            name = st.text_input(
                "Full Name"
            )

            email = st.text_input(
                "Email"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            submit = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if submit:

            if not name.strip():

                st.error(
                    "Please enter your name."
                )

            elif not email.strip():

                st.error(
                    "Please enter your email."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                result = register_customer(
                    name.strip(),
                    email.strip(),
                    password
                )

                if result["success"]:

                    # -------------------------------------
                    # SAVE CUSTOMER PROFILE IN SESSION
                    # -------------------------------------

                    st.session_state.customer_logged_in = True

                    st.session_state.customer_name = name.strip()

                    st.session_state.customer_email = email.strip()

                    st.session_state.customer_user_id = result["localId"]

                    st.session_state.id_token = result["idToken"]

                    st.success(
                        "Account created successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        result["error"]
                    )


    # =====================================================
    # CUSTOMER LOGIN
    # =====================================================

    elif account_page == "Login":

        st.header(
            "Customer Login"
        )

        st.caption(
            "Login to access Chat Support, "
            "Register Complaint and Check Status."
        )

        with st.form(
            "customer_login"
        ):

            email = st.text_input(
                "Email"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            login = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login:

            if not email.strip() or not password:

                st.error(
                    "Please enter email and password."
                )

            else:

                result = login_customer(
                    email.strip(),
                    password
                )

                if result["success"]:

                    st.session_state.customer_logged_in = True

                    st.session_state.customer_email = (
                        result["email"]
                    )

                    st.session_state.customer_user_id = (
                        result["localId"]
                    )

                    st.session_state.id_token = (
                        result["idToken"]
                    )

                    # Firebase Auth does not return
                    # the profile name here.
                    st.session_state.customer_name = (
                        email.split("@")[0]
                    )

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        result["error"]
                    )


    # =====================================================
    # ADMIN LOGIN
    # =====================================================

    else:

        st.header(
            "Staff / Admin"
        )

        st.caption(
            "Authorized staff only."
        )

        password = st.text_input(
            "Admin Password",
            type="password"
        )

        if st.button(
            "Admin Login",
            use_container_width=True
        ):

            try:

                admin_password = st.secrets[
                    "ADMIN_PASSWORD"
                ]

            except Exception:

                admin_password = "admin123"

            if password == admin_password:

                st.session_state.admin_logged_in = True

                st.rerun()

            else:

                st.error(
                    "Invalid admin password."
                )


    # =====================================================
    # ADMIN DASHBOARD WHILE CUSTOMER LOGGED OUT
    # =====================================================

    if st.session_state.admin_logged_in:

        st.markdown("---")

        if st.button(
            "Logout Admin"
        ):

            st.session_state.admin_logged_in = False

            st.rerun()

        admin_dashboard()


# =========================================================
# CUSTOMER IS LOGGED IN
# =========================================================

else:

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.image(
        "images/logo.png",
        width=130
    )

    st.sidebar.success(
        f"Logged in as {st.session_state.customer_name}"
    )

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Customer Menu",
        [
            "Chat Support",
            "Register Complaint",
            "Check Status"
        ]
    )

    st.sidebar.markdown("---")

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.customer_logged_in = False

        st.session_state.customer_name = ""

        st.session_state.customer_email = ""

        st.session_state.customer_user_id = ""

        st.session_state.id_token = ""

        st.session_state.messages = []

        st.session_state.waiting_for_name = False

        st.session_state.waiting_for_complaint = False

        st.rerun()


    # =====================================================
    # CHAT SUPPORT
    # =====================================================

    if page == "Chat Support":

        st.header(
            "Chat Support"
        )

        st.caption(
            "Ask anything about AppInSnap or report a problem."
        )

        # -----------------------------------------------
        # SHOW HISTORY
        # -----------------------------------------------

        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.write(
                    message["content"]
                )

        # -----------------------------------------------
        # CHAT INPUT
        # -----------------------------------------------

        question = st.chat_input(
            "Ask about AppInSnap..."
        )

        if question:

            question = question.strip()

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            with st.chat_message("user"):

                st.write(question)

            # ===========================================
            # COMPLAINT DETAILS
            # ===========================================

            if st.session_state.waiting_for_complaint:

                complaint = question

                name = st.session_state.customer_name

                email = st.session_state.customer_email

                user_id = st.session_state.customer_user_id

                try:

                    complaint_id = register_complaint(
                        name,
                        complaint,
                        email,
                        user_id
                    )

                    st.session_state.waiting_for_complaint = False

                    response = (
                        "Complaint registered successfully!\n\n"
                        f"**Complaint ID:** `{complaint_id}`\n\n"
                        "**Status:** Pending\n\n"
                        "You can check your complaint status "
                        "from the **Check Status** page."
                    )

                    with st.chat_message(
                        "assistant"
                    ):

                        st.success(
                            response
                        )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response
                        }
                    )

                except Exception as e:

                    with st.chat_message(
                        "assistant"
                    ):

                        st.error(
                            f"Unable to register complaint: {e}"
                        )


            # ===========================================
            # NEW COMPLAINT DETECTED
            # ===========================================

            elif is_complaint(question):

                st.session_state.waiting_for_complaint = True

                response = (
                    "I'm sorry you're experiencing a problem. "
                    "I can help you register a complaint.\n\n"
                    f"Since you are logged in as "
                    f"**{st.session_state.customer_name}**, "
                    "I already have your name.\n\n"
                    "**Please describe your complaint in detail.**"
                )

                with st.chat_message(
                    "assistant"
                ):

                    st.write(
                        response
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )


            # ===========================================
            # NORMAL RAG QUESTION
            # ===========================================

            else:

                with st.chat_message(
                    "assistant"
                ):

                    with st.spinner(
                        "Thinking..."
                    ):

                        answer = answer_question(
                            question
                        )

                    st.write(
                        answer
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


    # =====================================================
    # REGISTER COMPLAINT
    # =====================================================

    elif page == "Register Complaint":

        st.header(
            "Register Complaint"
        )

        st.caption(
            "Your account information will be attached automatically."
        )

        st.info(
            f"Customer: {st.session_state.customer_name}"
        )

        st.info(
            f"Email: {st.session_state.customer_email}"
        )

        with st.form(
            "customer_complaint"
        ):

            complaint = st.text_area(
                "Complaint Details",
                placeholder="Describe your problem...",
                height=160
            )

            submit = st.form_submit_button(
                "Submit Complaint",
                use_container_width=True
            )

        if submit:

            if not complaint.strip():

                st.error(
                    "Please describe your complaint."
                )

            else:

                try:

                    complaint_id = register_complaint(
                        st.session_state.customer_name,
                        complaint.strip(),
                        st.session_state.customer_email,
                        st.session_state.customer_user_id
                    )

                    st.success(
                        "Complaint registered successfully!"
                    )

                    st.info(
                        f"""
**Complaint ID:** `{complaint_id}`

**Status:** Pending

Please save this Complaint ID.
"""
                    )

                except Exception as e:

                    st.error(
                        f"Unable to register complaint: {e}"
                    )


    # =====================================================
    # CHECK STATUS
    # =====================================================

    elif page == "Check Status":

        st.header(
            "Check Complaint Status"
        )

        st.caption(
            "Only your own complaints are shown here."
        )

        try:

            complaints = get_customer_complaints(
                st.session_state.customer_user_id
            )

        except Exception as e:

            st.error(
                f"Unable to load your complaints: {e}"
            )

            complaints = []

        if not complaints:

            st.info(
                "You have not registered any complaints yet."
            )

        else:

            for complaint in complaints:

                with st.container(
                    border=True
                ):

                    st.write(
                        f"**Complaint ID:** "
                        f"`{complaint.get('complaint_id', '')}`"
                    )

                    st.write(
                        f"**Complaint:** "
                        f"{complaint.get('complaint', '')}"
                    )

                    status = complaint.get(
                        "status",
                        "Pending"
                    )

                    if status == "Resolved":

                        st.success(
                            f"Status: {status}"
                        )

                    elif status == "In Progress":

                        st.info(
                            f"Status: {status}"
                        )

                    else:

                        st.warning(
                            f"Status: {status}"
                        )