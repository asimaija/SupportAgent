import base64
import streamlit as st
from agents.support_agent import answer_question


st.set_page_config(
    page_title="AppInSnap Support",
    page_icon="⚡",
    layout="centered"
)


# --------------------------------
# Load logo as base64
# --------------------------------
def load_logo_base64(path="images/logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


logo_b64 = load_logo_base64()


# --------------------------------
# Design system
# Palette drawn from the AppInSnap mark:
# ink #1A162A, violet #4A2FD1 -> indigo #405CEB
# --------------------------------
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
        :root {
            --ink: #1A162A;
            --muted: #6B6580;
            --violet: #4A2FD1;
            --indigo: #405CEB;
            --bg: #FAF9FC;
            --surface: #FFFFFF;
            --border: #EDEBF4;
            --lavender: #F1EFFB;
        }

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background: var(--bg); }

        .block-container {
            padding-top: 3.2rem;
            padding-bottom: 8rem;
            max-width: 700px;
        }

        /* ---- Top logo ---- */
        .header-row {
            display: flex;
            justify-content: center;
            margin-bottom: 1.6rem;
        }
        .header-row img {
            height: 34px;
            width: auto;
        }

        /* ---- Sidebar ---- */
        [data-testid="stSidebar"] {
            background: var(--surface);
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }
        .sidebar-logo {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 1.6rem;
        }
        .sidebar-logo img {
            height: 22px;
            width: auto;
        }
        .sidebar-label {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            color: var(--muted);
            margin: 0.4rem 0 0.7rem 0;
        }
        [data-testid="stSidebar"] div[data-testid="stButton"] > button {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--ink);
            font-weight: 500;
            font-size: 0.86rem;
            text-align: left;
            padding: 0.55rem 0.85rem;
            white-space: normal;
            line-height: 1.3;
        }
        [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            border-color: var(--violet);
            background: var(--lavender);
            color: var(--violet);
        }

        /* ---- Empty-state greeting ---- */
        .greeting-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding-top: 3rem;
            padding-bottom: 1rem;
        }
        .greeting-icon {
            width: 46px;
            height: 46px;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--violet), var(--indigo));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            margin-bottom: 1.2rem;
        }
        .greeting-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.9rem;
            font-weight: 600;
            color: var(--ink);
            margin-bottom: 0.5rem;
        }
        .greeting-sub {
            color: var(--muted);
            font-size: 0.98rem;
        }

        /* ---- Chat messages: user bubble right, assistant plain left ---- */
        [data-testid="stChatMessage"] {
            background: transparent !important;
            border: none !important;
            padding: 0.3rem 0 !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            flex-direction: row-reverse;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
            background: var(--lavender);
            border-radius: 16px;
            padding: 0.6rem 1rem;
            max-width: 78%;
            margin-left: auto;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageAvatarUser"] {
            display: none;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageAvatarAssistant"] {
            background: linear-gradient(135deg, var(--violet), var(--indigo)) !important;
            width: 28px;
            height: 28px;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
            color: var(--ink);
            padding-top: 0.15rem;
        }

        /* ---- Chat input: pill, docked bottom ---- */
        [data-testid="stChatInput"] {
            max-width: 700px;
            margin: 0 auto;
        }
        [data-testid="stChatInput"] > div {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 26px;
            box-shadow: 0 2px 10px rgba(26, 22, 42, 0.05);
        }
        [data-testid="stChatInput"] textarea {
            font-family: 'Inter', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)


# --------------------------------
# Top logo (above sidebar + main area)
# --------------------------------
if logo_b64:
    st.markdown(
        f'<div class="header-row"><img src="data:image/png;base64,{logo_b64}" /></div>',
        unsafe_allow_html=True
    )


# --------------------------------
# Chat state
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
# Sidebar: questions on top, clear chat below
# --------------------------------
with st.sidebar:
    if logo_b64:
        st.markdown(
            f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_b64}" /></div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="sidebar-label">Try asking</div>', unsafe_allow_html=True)

    for q in example_questions:
        if st.button(q, use_container_width=True):
            pending_question = q

    st.markdown("<div style='height: 0.9rem'></div>", unsafe_allow_html=True)

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --------------------------------
# Main area (right side): greeting + chat
# --------------------------------
if not st.session_state.messages:
    st.markdown(
        '''
        <div class="greeting-wrap">
            <div class="greeting-icon">⚡</div>
            <div class="greeting-title">How can I help?</div>
            <div class="greeting-sub">Ask anything about AppInSnap</div>
        </div>
        ''',
        unsafe_allow_html=True
    )


# --------------------------------
# Render chat history
# --------------------------------
for message in st.session_state.messages:
    avatar = "⚡" if message["role"] == "assistant" else "🙂"
    with st.chat_message(message["role"], avatar=avatar):
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

    with st.chat_message("user", avatar="🙂"):
        st.write(question)

    with st.chat_message("assistant", avatar="⚡"):

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