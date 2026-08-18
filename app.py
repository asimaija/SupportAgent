import streamlit as st

from agents.support_agent import answer_question
from data.complaints import (
    register_complaint,
    get_complaint,
    update_complaint_status
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AppInSnap Support",
    page_icon="⚡",
    layout="centered"
)


# =========================================================
# SIMPLE DESIGN
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 850px;
        padding-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([4, 1])

with col1:
    st.title("AppInSnap Support")

with col2:
    st.image(
        "images/logo.png",
        width=110
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.image(
        "images/logo.png",
        width=130
    )

    page = st.radio(
        "Menu",
        [
            "Chat Support",
            "Register Complaint",
            "Check Status",
            "Manage Complaint"
        ]
    )


# =========================================================
# CHAT SUPPORT
# =========================================================

if page == "Chat Support":

    st.header("Chat Support")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for m in st.session_state.messages:

        with st.chat_message(m["role"]):
            st.write(m["content"])

    # Chat input
    q = st.chat_input(
        "Type your question..."
    )

    if q:

        # Add user message to history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": q
            }
        )

        # Display user message
        with st.chat_message("user"):
            st.write(q)

        # Assistant response
        with st.chat_message("assistant"):

            # Show Thinking while generating answer
            with st.spinner("Thinking..."):

                answer = answer_question(q)

            # Display answer
            st.write(answer)

        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# =========================================================
# REGISTER COMPLAINT
# =========================================================

elif page == "Register Complaint":

    st.header("Register Complaint")

    with st.form("complaint"):

        name = st.text_input(
            "Name"
        )

        text = st.text_area(
            "Complaint"
        )

        submit = st.form_submit_button(
            "Submit"
        )

    if submit:

        if not name or not text:

            st.error(
                "Please fill all fields."
            )

        else:

            cid = register_complaint(
                name,
                text
            )

            st.success(
                "Complaint registered successfully!"
            )

            st.info(
                f"Complaint ID: {cid}\n\n"
                "Status: Pending"
            )


# =========================================================
# CHECK COMPLAINT STATUS
# =========================================================

elif page == "Check Status":

    st.header(
        "Check Complaint Status"
    )

    cid = st.text_input(
        "Complaint ID"
    )

    if st.button("Check"):

        c = get_complaint(
            cid.strip().upper()
        )

        if c:

            st.write(
                f"**ID:** "
                f"{c.get('complaint_id', cid)}"
            )

            st.write(
                f"**Name:** "
                f"{c.get('name', '')}"
            )

            st.write(
                f"**Complaint:** "
                f"{c.get('complaint', '')}"
            )

            st.success(
                f"Status: "
                f"{c.get('status', 'Pending')}"
            )

        else:

            st.error(
                "Complaint not found."
            )


# =========================================================
# MANAGE COMPLAINT
# =========================================================

else:

    st.header(
        "Manage Complaint"
    )

    cid = st.text_input(
        "Complaint ID"
    )

    if st.button("Find"):

        c = get_complaint(
            cid.strip().upper()
        )

        if c:

            st.session_state.complaint = c

        else:

            st.session_state.complaint = None

            st.error(
                "Complaint not found."
            )

    # Get complaint from session
    c = st.session_state.get(
        "complaint"
    )

    if c:

        st.write(
            f"**ID:** "
            f"{c.get('complaint_id', cid)}"
        )

        st.write(
            f"**Name:** "
            f"{c.get('name', '')}"
        )

        st.write(
            f"**Complaint:** "
            f"{c.get('complaint', '')}"
        )

        st.write(
            f"**Current:** "
            f"{c.get('status', 'Pending')}"
        )

        # Status selection
        status = st.selectbox(
            "New Status",
            [
                "Pending",
                "In Progress",
                "Resolved"
            ]
        )

        # Update complaint
        if st.button("Update"):

            complaint_id = c.get(
                "complaint_id",
                cid.upper()
            )

            update_complaint_status(
                complaint_id,
                status
            )

            # Refresh complaint data
            st.session_state.complaint = get_complaint(
                complaint_id
            )

            st.success(
                f"Updated: {status}"
            )