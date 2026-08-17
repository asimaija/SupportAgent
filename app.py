import streamlit as st

from agents.support_agent import answer_question
from data.complaints import register_complaint


st.set_page_config(
    page_title="AppInSnap Support",
    page_icon="⚡",
    layout="centered"
)


# -----------------------------
# Simple design
# -----------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f8f7fc;
    }

    .title {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Logo
# -----------------------------

st.image(
    "images/logo.png",
    width=160
)


st.markdown(
    '<div class="title">Support</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">We are here to help you</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Session state
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.image(
        "images/logo.png",
        width=130
    )

    st.divider()

    page = st.radio(
        "Choose an option",
        [
            "Chat Support",
            "Register Complaint"
        ]
    )


# =============================
# CHAT SUPPORT
# =============================

if page == "Chat Support":

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    question = st.chat_input(
        "Type your question..."
    )


    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })


        with st.chat_message("user"):
            st.write(question)


        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                answer = answer_question(
                    question
                )

            st.write(answer)


        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()


# =============================
# REGISTER COMPLAINT
# =============================

else:

    st.subheader("Register Complaint")

    st.write(
        "Please provide the details of your complaint."
    )


    with st.form("complaint_form"):

        name = st.text_input(
            "Name"
        )

        complaint = st.text_area(
            "Complaint",
            placeholder="Write your complaint here..."
        )


        submit = st.form_submit_button(
            "Submit Complaint"
        )


        if submit:

            if not name.strip():

                st.error(
                    "Please enter your name."
                )

            elif not complaint.strip():

                st.error(
                    "Please enter your complaint."
                )

            else:

                complaint_id = register_complaint(
                    name.strip(),
                    complaint.strip()
                )


                st.success(
                    "Complaint registered successfully!"
                )


                st.info(
                    f"Complaint ID: {complaint_id}\n\n"
                    "Status: Pending"
                )