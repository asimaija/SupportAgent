import streamlit as st
from agents.support_agent import answer_question
from data.complaints import (
    register_complaint,
    get_complaint,
    update_complaint_status
)

st.set_page_config(page_title="AppInSnap Support", page_icon="⚡")

# Simple design
st.markdown("""
<style>
.block-container {max-width:850px;padding-top:25px}
.logo {text-align:right}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([4, 1])

with col1:
    st.title("AppInSnap Support")

with col2:
    st.image("images/logo.png", width=110)

# Sidebar
with st.sidebar:
    st.image("images/logo.png", width=130)
    page = st.radio(
        "Menu",
        ["Chat Support", "Register Complaint",
         "Check Status", "Manage Complaint"]
    )


# ================= CHAT =================

if page == "Chat Support":

    st.header("Chat Support")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    q = st.chat_input("Type your question...")

    if q:
        st.session_state.messages.append({"role": "user", "content": q})

        with st.chat_message("user"):
            st.write(q)

        answer = answer_question(q)

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )


# ================= REGISTER =================

elif page == "Register Complaint":

    st.header("Register Complaint")

    with st.form("complaint"):

        name = st.text_input("Name")
        text = st.text_area("Complaint")

        submit = st.form_submit_button("Submit")

    if submit:

        if not name or not text:
            st.error("Please fill all fields.")

        else:
            cid = register_complaint(name, text)

            st.success("Complaint registered successfully!")
            st.info(f"Complaint ID: {cid}\n\nStatus: Pending")


# ================= CHECK STATUS =================

elif page == "Check Status":

    st.header("Check Complaint Status")

    cid = st.text_input("Complaint ID")

    if st.button("Check"):

        c = get_complaint(cid.strip().upper())

        if c:
            st.write(f"**ID:** {c.get('complaint_id', cid)}")
            st.write(f"**Name:** {c.get('name', '')}")
            st.write(f"**Complaint:** {c.get('complaint', '')}")
            st.success(f"Status: {c.get('status', 'Pending')}")
        else:
            st.error("Complaint not found.")


# ================= MANAGE =================

else:

    st.header("Manage Complaint")

    cid = st.text_input("Complaint ID")

    if st.button("Find"):

        c = get_complaint(cid.strip().upper())

        if c:
            st.session_state.complaint = c
        else:
            st.session_state.complaint = None
            st.error("Complaint not found.")

    c = st.session_state.get("complaint")

    if c:

        st.write(f"**ID:** {c.get('complaint_id', cid)}")
        st.write(f"**Name:** {c.get('name', '')}")
        st.write(f"**Complaint:** {c.get('complaint', '')}")
        st.write(f"**Current:** {c.get('status', 'Pending')}")

        status = st.selectbox(
            "New Status",
            ["Pending", "In Progress", "Resolved"]
        )

        if st.button("Update"):

            complaint_id = c.get("complaint_id", cid.upper())

            update_complaint_status(
                complaint_id,
                status
            )

            st.session_state.complaint = get_complaint(
                complaint_id
            )

            st.success(f"Updated: {status}")