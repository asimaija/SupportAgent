import streamlit as st

from agents.agent import ask_agent
from agents.tools import set_customer_context

from data.complaints import (
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

    /* -----------------------------------------------------
       MAIN CONTAINER
    ----------------------------------------------------- */

    .block-container {
        max-width: 850px;
        padding-top: 25px;
        padding-bottom: 40px;
    }


    /* -----------------------------------------------------
       GENERAL TEXT
    ----------------------------------------------------- */

    body {
        color: #000000;
    }

    p {
        color: #000000;
    }


    /* -----------------------------------------------------
       CHAT TEXT
    ----------------------------------------------------- */

    [data-testid="stChatMessage"] {
        color: #000000 !important;
    }

    [data-testid="stChatMessage"] p {
        color: #000000 !important;
        line-height: 1.6;
    }

    [data-testid="stChatMessage"] li {
        color: #000000 !important;
        line-height: 1.6;
    }

    [data-testid="stChatMessage"] strong {
        color: #000000 !important;
        font-weight: 700;
    }

    [data-testid="stChatMessage"] em {
        color: #000000 !important;
    }


    /* -----------------------------------------------------
       BUTTON
    ----------------------------------------------------- */

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


    /* -----------------------------------------------------
       CHAT INPUT
    ----------------------------------------------------- */

    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #777777 !important;
    }


    /* -----------------------------------------------------
       STATUS COLORS
    ----------------------------------------------------- */

    .status-pending {
        color: #A87A1D;
        font-weight: 700;
    }

    .status-progress {
        color: #3B4CE0;
        font-weight: 700;
    }

    .status-resolved {
        color: #1C8A5E;
        font-weight: 700;
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

    "admin_logged_in": False
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

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    st.sidebar.image(
        "images/logo.png",
        width=130
    )

    st.sidebar.markdown("---")

    account_page = st.sidebar.radio(
        "Account Menu",
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


        # -------------------------------------------------
        # REGISTER PROCESS
        # -------------------------------------------------

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

                if result.get("success"):

                    st.session_state.customer_logged_in = True

                    st.session_state.customer_name = (
                        name.strip()
                    )

                    st.session_state.customer_email = (
                        email.strip()
                    )

                    st.session_state.customer_user_id = (
                        result.get("localId", "")
                    )

                    st.session_state.id_token = (
                        result.get("idToken", "")
                    )

                    st.session_state.messages = []

                    st.success(
                        "Account created successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        result.get(
                            "error",
                            "Registration failed."
                        )
                    )


    # =====================================================
    # CUSTOMER LOGIN
    # =====================================================

    elif account_page == "Login":

        st.header(
            "Customer Login"
        )

        st.caption(
            "Login to access Chat Support "
            "and Check Status."
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


        # -------------------------------------------------
        # LOGIN PROCESS
        # -------------------------------------------------

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

                if result.get("success"):

                    st.session_state.customer_logged_in = True

                    st.session_state.customer_email = (
                        result.get(
                            "email",
                            email.strip()
                        )
                    )

                    st.session_state.customer_user_id = (
                        result.get(
                            "localId",
                            ""
                        )
                    )

                    st.session_state.id_token = (
                        result.get(
                            "idToken",
                            ""
                        )
                    )

                    # Firebase login response doesn't
                    # contain the profile name.
                    st.session_state.customer_name = (
                        email.split("@")[0]
                    )

                    st.session_state.messages = []

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        result.get(
                            "error",
                            "Login failed."
                        )
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

                # Development fallback only
                admin_password = "admin123"


            if password == admin_password:

                st.session_state.admin_logged_in = True

                st.rerun()

            else:

                st.error(
                    "Invalid admin password."
                )


    # =====================================================
    # ADMIN DASHBOARD
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
# CUSTOMER LOGGED IN
# =========================================================

else:

    # =====================================================
    # CUSTOMER SIDEBAR
    # =====================================================

    st.sidebar.image(
        "images/logo.png",
        width=130
    )

    st.sidebar.success(
        f"Logged in as "
        f"{st.session_state.customer_name}"
    )

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Customer Menu",
        [
            "Chat Support",
            "Check Status"
        ]
    )

    st.sidebar.markdown("---")


    # =====================================================
    # LOGOUT
    # =====================================================

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


        # -------------------------------------------------
        # DISPLAY CHAT HISTORY
        # -------------------------------------------------

        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )


        # -------------------------------------------------
        # CHAT INPUT
        # -------------------------------------------------

        question = st.chat_input(
            "Ask about AppInSnap..."
        )


        if question:

            question = question.strip()


            # ---------------------------------------------
            # SAVE USER MESSAGE
            # ---------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )


            with st.chat_message(
                "user"
            ):

                st.markdown(
                    question
                )


            # ---------------------------------------------
            # SET CUSTOMER CONTEXT
            # ---------------------------------------------

            set_customer_context(

                name=(
                    st.session_state.customer_name
                ),

                email=(
                    st.session_state.customer_email
                ),

                user_id=(
                    st.session_state.customer_user_id
                )
            )


            # ---------------------------------------------
            # LANGCHAIN AGENT
            # ---------------------------------------------

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "Thinking..."
                ):

                    try:

                        answer = ask_agent(

                            question=question,

                            customer_name=(
                                st.session_state.customer_name
                            ),

                            customer_email=(
                                st.session_state.customer_email
                            ),

                            customer_user_id=(
                                st.session_state.customer_user_id
                            )
                        )


                    except Exception as e:

                        answer = (
                            "Sorry, I was unable to "
                            "process your request.\n\n"
                            f"Error: {str(e)}"
                        )


                st.markdown(
                    answer
                )


            # ---------------------------------------------
            # SAVE ASSISTANT MESSAGE
            # ---------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
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


        # -------------------------------------------------
        # GET CUSTOMER COMPLAINTS
        # -------------------------------------------------

        try:

            complaints = get_customer_complaints(
                st.session_state.customer_user_id
            )

        except Exception as e:

            st.error(
                f"Unable to load your complaints: {e}"
            )

            complaints = []


        # -------------------------------------------------
        # NO COMPLAINTS
        # -------------------------------------------------

        if not complaints:

            st.info(
                "You have not registered "
                "any complaints yet."
            )


        # -------------------------------------------------
        # DISPLAY COMPLAINTS
        # -------------------------------------------------

        else:

            for complaint in complaints:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"**Complaint ID:** "
                        f"`{complaint.get('complaint_id', '')}`"
                    )


                    st.markdown(
                        f"**Complaint:** "
                        f"{complaint.get('complaint', '')}"
                    )


                    status = complaint.get(
                        "status",
                        "Pending"
                    )


                    # -------------------------------------
                    # STATUS DISPLAY
                    # -------------------------------------

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