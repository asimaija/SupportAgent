import base64
import streamlit as st
from agents.support_agent import answer_question


st.set_page_config(
    page_title="AppInSnap Support",
    page_icon="🤖",
    layout="centered"
)


# --------------------------------
# Load logo as base64 (for reliable inline alignment)
# --------------------------------
def load_logo_base64(path="images/logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


logo_b64 = load_logo_base64()


# --------------------------------
# Simple custom styling
# --------------------------------
st.markdown("""
    <style>
        .block-container {
            padding-top: 2.5rem;
            max-width: 820px;
        }
        [data-testid="stChatMessage"] {
            border-radius: 14px;
            padding: 4px 2px;
        }
        .header-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 0.3rem;
        }
        .header-row img {
            height: 40px;
            width: auto;
        }
        .subtitle {
            color: #6b7280;
            font-size: 0.95rem;
            margin-bottom: 1.8rem;
        }
        .panel {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 1.3rem 1.4rem;
            height: 100%;
        }
        .panel h4 {
            margin-top: 0;
            margin-bottom: 0.6rem;
            font-size: 1rem;
            color: #111827;
        }
        .panel p {
            color: #4b5563;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        [data-testid="stSidebar"] .sidebar-logo {
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
        }
        [data-testid="stSidebar"] .sidebar-logo img {
            height: 34px;
            width: auto;
        }
    </style>
""", unsafe_allow_html=True)


# --------------------------------
# Header
# --------------------------------
if logo_b64:
    st.markdown(
        f'<div class="header-row"><img src="data:image/png;base64,{logo_b64}" /></div>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<div class="header-row"><b>AppInSnap Support</b></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Ask anything about AppInSnap — I\'ll do my best to help.</div>',
    unsafe_allow_html=True
)


# --------------------------------
# Sidebar (kept minimal: logo + clear chat)
# --------------------------------
with st.sidebar:
    if logo_b64:
        st.markdown(
            f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_b64}" /></div>',
            unsafe_allow_html=True
        )
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --------------------------------
# Chat history state
# --------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

pending_question = None

example_questions = [
    "What is AppInSnap?",
    "How do I create an account?",
    "How do I reset my password?",
    "What features does AppInSnap offer?",
]

# --------------------------------
# Welcome layout (only before first message) — fills empty space
# --------------------------------
if not st.session_state.messages:

    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        for q in example_questions:
            if st.button(q, use_container_width=True):
                pending_question = q

    with right_col:
        st.markdown(
            '''
            <div class="panel">
                <h4>ℹ️ About</h4>
                <p>This assistant answers questions using AppInSnap's
                knowledge base. If it doesn't know something, it'll
                say so rather than guess.</p>
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.write("")


# --------------------------------
# Render chat history
# --------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# --------------------------------
# Handle new input
# --------------------------------
typed_question = st.chat_input("Ask about AppInSnap...")

question = pending_question or typed_question

if question:

    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:
                answer = answer_question(question)

            except Exception as e:
                answer = f"⚠️ Something went wrong: {e}"

        st.write(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    st.rerun()