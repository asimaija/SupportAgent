import streamlit as st
import textwrap
import re
from pathlib import Path

from agents.support_agent import answer_question
from agents.complaint_detector import is_complaint

from data.complaints import (
    register_complaint,
    get_customer_complaints
)

from customer.auth import (
    register_customer,
    login_customer,
    login_firebase_user
)

from data.admin_auth import is_admin
from admin.admin_dashboard import admin_dashboard


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AppInSnap Support",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# COLORS  ("Signal Blue" theme — light, professional, B2B-tech)
# =========================================================

BG = "#F6F5FC"           # soft violet-white page background
SIDEBAR = "#FFFFFF"
CARD = "#FFFFFF"
CARD_HOVER = "#F1EEFF"
BORDER = "#E4E0F5"

ACCENT = "#4F35E0"        # primary brand indigo/violet, sampled from the logo mark
ACCENT_DARK = "#3820B8"
ACCENT_SOFT = "#EEEBFF"   # light violet tint for subtle fills
TEAL = "#12B8A6"          # secondary accent

WHITE = "#FFFFFF"
TEXT = "#1A162A"          # near-navy, matches the logo wordmark
MUTED = "#6B7787"

GREEN = "#16A34A"
YELLOW = "#D97706"
RED = "#DC2626"


# =========================================================
# LOGO
# =========================================================

LOGO_PATH = Path(__file__).resolve().parent / "images" / "logo.png"

# Small square crop of just the icon mark (no wordmark text) — this is
# what goes in tight spots like the header and sidebar, where the full
# wide logo.png gets squeezed into an illegible smudge. Falls back to
# the full logo if this hasn't been generated yet.
LOGO_MARK_PATH = Path(__file__).resolve().parent / "images" / "logo_mark.png"

# All-white version of the icon mark, for use on top of the brand-colored
# header banner where the regular indigo mark would blend in and disappear.
LOGO_MARK_WHITE_PATH = Path(__file__).resolve().parent / "images" / "logo_mark_white.png"


# =========================================================
# HTML HELPER
# =========================================================

def build_complaint_card_html(complaint_id, complaint_text, status, customer_name):
    """
    Returns the HTML string for the "complaint registered" confirmation
    card shown in chat right after a complaint is filed.
    """

    preview = complaint_text.strip()

    if len(preview) > 220:

        preview = preview[:220].rstrip() + "…"

    return f"""
    <div class="complaint-confirm-card">
        <div class="complaint-confirm-title">
            ✅ Complaint Registered
        </div>
        <div class="complaint-confirm-row">
            <span class="complaint-confirm-label">Complaint ID</span>
            <span class="complaint-confirm-value">{complaint_id}</span>
        </div>
        <div class="complaint-confirm-row">
            <span class="complaint-confirm-label">Submitted by</span>
            <span class="complaint-confirm-value">{customer_name}</span>
        </div>
        <div class="complaint-confirm-row">
            <span class="complaint-confirm-label">Status</span>
            <span class="complaint-confirm-value">{status}</span>
        </div>
        <div class="complaint-confirm-row">
            <span class="complaint-confirm-label">Details</span>
            <span class="complaint-confirm-value">{preview}</span>
        </div>
    </div>
    """


def strip_bold(text):
    """
    Strips markdown bold markers (**word** / __word__) so answers and
    labels render as plain text everywhere in the app — bolded words
    inside generated answers don't look good mixed into normal prose.
    """

    if not text:

        return text

    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)

    text = re.sub(r"__(.+?)__", r"\1", text)

    return text


def render_html(content):

    text = textwrap.dedent(content)

    # Blank lines inside a raw HTML block make Streamlit's markdown
    # parser stop treating the rest as HTML and render it as a code
    # block instead. Stripping blank lines keeps it as real HTML.
    lines = [
        line for line in text.split("\n")
        if line.strip() != ""
    ]

    st.markdown(
        "\n".join(lines),
        unsafe_allow_html=True
    )


# =========================================================
# CSS
# =========================================================

render_html(
    f"""
    <style>

    /* =====================================================
       GLOBAL
    ===================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    .stApp {{

        background: {BG} !important;

        color: {TEXT} !important;

        font-family: -apple-system, "Segoe UI", Inter, sans-serif;

        font-size: 16px;
    }}


    .main {{

        background: {BG} !important;
    }}


    .block-container {{

        max-width: 1080px !important;

        padding-top: 24px !important;

        padding-bottom: 100px !important;
    }}


    [data-testid="stHeader"] {{

        background: {BG} !important;
    }}


    [data-testid="stToolbar"] {{

        display: none !important;
    }}


    footer {{

        display: none !important;
    }}


    /* =====================================================
       SIDEBAR
    ===================================================== */

    [data-testid="stSidebar"] {{

        background: {SIDEBAR} !important;

        border-right: 1px solid {BORDER} !important;

        min-width: 270px !important;

        max-width: 270px !important;

        margin-left: 0px !important;

        transform: none !important;

        visibility: visible !important;
    }}


    /* Force the sidebar to always stay open — hide the collapse
       control so "Chat Support / Check Status" can't be tucked
       away out of sight. */

    [data-testid="collapsedControl"] {{

        display: none !important;
    }}


    [data-testid="stSidebar"] > div:first-child {{

        background: {SIDEBAR} !important;

        padding-top: 20px !important;
    }}


    [data-testid="stSidebar"] * {{

        color: {TEXT};
    }}


    [data-testid="stSidebar"] [data-testid="stRadio"] label {{

        background: transparent !important;

        border-radius: 10px !important;

        padding: 10px 12px !important;

        margin-bottom: 5px !important;

        color: {TEXT} !important;

        font-size: 16px !important;
    }}


    [data-testid="stSidebar"] div.stButton > button {{

        font-size: 16px !important;

        padding: 10px 16px !important;
    }}


    /* Give the Logout buttons a bit more visual weight so they
       read as distinct, deliberate actions in the sidebar. */

    .st-key-customer_logout button,
    .st-key-admin_logout button {{

        border-color: {RED} !important;

        color: {RED} !important;

        font-weight: 600 !important;
    }}


    .st-key-customer_logout button:hover,
    .st-key-admin_logout button:hover {{

        background: #FDECEC !important;

        border-color: {RED} !important;

        color: {RED} !important;
    }}


    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{

        background: {CARD} !important;
    }}


    /* =====================================================
       APP HEADER
    ===================================================== */

    .app-header {{

        height: 70px;

        display: flex;

        align-items: center;

        padding: 0 10px;

        border-bottom: 1px solid {BORDER};

        margin-bottom: 30px;
    }}


    .app-logo {{

        width: 40px;

        height: 40px;

        object-fit: contain;

        margin-right: 14px;
    }}


    .app-title {{

        color: {WHITE};

        font-size: 22px;

        font-weight: 700;

        letter-spacing: -0.4px;

        line-height: 48px;

        white-space: nowrap;
    }}


    .header-spacer {{

        flex: 1;
    }}


    .header-user {{

        color: {WHITE};

        font-size: 15px;

        font-weight: 600;

        line-height: 48px;

        white-space: nowrap;

        overflow: visible;

        text-align: right;
    }}


    /* Colored banner behind the top header row (logo / title / user)
       so it always sits on the brand color with white text, on every
       page — landing, chat, and admin alike. */

    div[data-testid="stHorizontalBlock"]:has(.app-header-bar) {{

        background: {ACCENT};

        border-radius: 14px;

        padding: 10px 20px !important;

        margin-bottom: 26px !important;
    }}


    /* =====================================================
       WELCOME
    ===================================================== */

    .welcome {{

        text-align: center;

        margin-top: 60px;

        margin-bottom: 40px;
    }}


    .welcome h1 {{

        color: {TEXT} !important;

        font-size: 38px !important;

        font-weight: 700 !important;

        letter-spacing: -1px;

        margin-bottom: 10px !important;
    }}


    .welcome p {{

        color: {MUTED} !important;

        font-size: 16px;

        margin: 0 !important;
    }}


    /* =====================================================
       LANDING MENU CARDS (Customer / Admin)
    ===================================================== */

    .landing-wrap {{

        max-width: 620px;

        margin: 0 auto;
    }}


    div.stButton {{

        margin-bottom: 12px !important;
    }}


    div.stButton > button {{

        width: 100% !important;

        background: {CARD} !important;

        color: {TEXT} !important;

        border: 1px solid {BORDER} !important;

        border-radius: 16px !important;

        padding: 16px 20px !important;

        font-size: 16px !important;

        font-weight: 500 !important;

        text-align: left !important;

        transition: all 0.15s ease !important;

        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04) !important;
    }}


    div.stButton > button:hover {{

        background: {CARD_HOVER} !important;

        border-color: {ACCENT} !important;

        color: {ACCENT_DARK} !important;

        box-shadow: 0 4px 12px rgba(79, 53, 224, 0.16) !important;
    }}


    div.stButton > button:focus {{

        color: {ACCENT_DARK} !important;

        border-color: {ACCENT} !important;

        box-shadow: 0 0 0 1px {ACCENT} !important;
    }}


    .menu-card {{

        min-height: 120px !important;

        font-size: 17px !important;
    }}


    /* =====================================================
       TABS (Login / Register)
    ===================================================== */

    [data-testid="stTabs"] button {{

        color: {MUTED} !important;

        font-weight: 600 !important;
    }}


    [data-testid="stTabs"] button[aria-selected="true"] {{

        color: {ACCENT} !important;

        border-bottom-color: {ACCENT} !important;
    }}


    /* =====================================================
       CHAT
    ===================================================== */

    [data-testid="stChatMessage"] {{

        background: transparent !important;

        color: {TEXT} !important;

        border: none !important;
    }}


    [data-testid="stChatMessageContent"] {{

        color: {TEXT} !important;
    }}


    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {{

        color: {TEXT} !important;

        font-size: 17px !important;

        line-height: 1.65 !important;
    }}


    [data-testid="stChatMessage"] strong {{

        color: {TEXT} !important;
    }}


    /* =====================================================
       CHAT INPUT
    ===================================================== */

    [data-testid="stChatInput"] {{

        background: {CARD} !important;

        border: 1px solid {BORDER} !important;

        border-radius: 22px !important;

        padding: 4px !important;
    }}


    [data-testid="stChatInput"] textarea {{

        background: {CARD} !important;

        color: {TEXT} !important;

        font-size: 16px !important;
    }}


    [data-testid="stChatInput"] textarea::placeholder {{

        color: #A5AEC0 !important;
    }}


    /* =====================================================
       INPUT FIELDS
    ===================================================== */

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {{

        background: {CARD} !important;

        color: {TEXT} !important;

        border: 1px solid {BORDER} !important;

        border-radius: 10px !important;
    }}


    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {{

        border-color: {ACCENT} !important;

        box-shadow: 0 0 0 1px {ACCENT} !important;
    }}


    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label {{

        color: {TEXT} !important;
    }}


    /* =====================================================
       PRIMARY BUTTON
    ===================================================== */

    button[kind="primary"] {{

        background: {ACCENT} !important;

        color: {WHITE} !important;

        border: none !important;

        border-radius: 10px !important;

        font-weight: 700 !important;
    }}


    button[kind="primary"]:hover {{

        background: {ACCENT_DARK} !important;
    }}


    /* =====================================================
       ACCOUNT PAGE
    ===================================================== */

    .account-title {{

        text-align: center;

        color: {TEXT};

        font-size: 32px;

        font-weight: 700;

        margin-top: 15px;

        margin-bottom: 6px;
    }}


    .account-subtitle {{

        text-align: center;

        color: {MUTED};

        font-size: 15px;

        margin-bottom: 30px;
    }}


    .back-link {{

        color: {MUTED};

        font-size: 14px;

        margin-bottom: 18px;
    }}


    /* =====================================================
       STATUS CARDS
    ===================================================== */

    .complaint-card {{

        background: {CARD};

        border: 1px solid {BORDER};

        border-radius: 16px;

        padding: 20px;

        margin-bottom: 15px;

        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
    }}


    /* Card used to confirm a newly-registered complaint in chat */

    .complaint-confirm-card {{

        background: {ACCENT_SOFT};

        border: 1px solid {ACCENT};

        border-radius: 16px;

        padding: 20px 22px;

        margin: 6px 0 4px 0;
    }}


    .complaint-confirm-title {{

        color: {ACCENT_DARK};

        font-size: 15px;

        font-weight: 700;

        display: flex;

        align-items: center;

        gap: 6px;

        margin-bottom: 12px;
    }}


    .complaint-confirm-row {{

        display: flex;

        justify-content: space-between;

        padding: 6px 0;

        border-bottom: 1px solid rgba(79, 53, 224, 0.16);
    }}


    .complaint-confirm-row:last-child {{

        border-bottom: none;
    }}


    .complaint-confirm-label {{

        color: {MUTED};

        font-size: 13px;
    }}


    .complaint-confirm-value {{

        color: {TEXT};

        font-size: 13px;

        font-weight: 600;

        text-align: right;

        max-width: 65%;
    }}


    .complaint-id {{

        color: {ACCENT};

        font-size: 16px;

        font-weight: 700;
    }}


    .complaint-description {{

        color: {TEXT};

        margin-top: 12px;

        line-height: 1.6;
    }}


    .complaint-status {{

        margin-top: 12px;

        color: {MUTED};
    }}


    /* =====================================================
       MOBILE
    ===================================================== */

    @media (max-width: 700px) {{

        .block-container {{

            padding-left: 15px !important;

            padding-right: 15px !important;
        }}


        .welcome h1 {{

            font-size: 28px !important;
        }}


        .app-title {{

            font-size: 19px;
        }}

    }}

    </style>
    """
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

    "waiting_for_complaint": False,

    "complaint_prompt_sent": False,

    "admin_logged_in": False,

    "admin_user_id": "",

    "admin_email": "",

    "admin_id_token": "",

    # Which top-level landing menu the visitor picked:
    # None -> show the Customer / Admin chooser
    # "customer" -> show Login / Register
    # "admin" -> show admin email/password form
    "account_view": None
}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# HEADER
# =========================================================

def show_header():

    col_logo, col_title, col_user = st.columns(
        [0.08, 0.52, 0.4]
    )

    with col_logo:

        # Invisible marker picked up by the `:has(.app-header-bar)` CSS
        # rule above, so this whole row gets the brand-colored banner
        # background on every page (landing, chat, and admin alike).
        # It has to live inside the columns block to be a descendant
        # of the stHorizontalBlock that :has() matches against.
        render_html('<div class="app-header-bar" style="display:none;"></div>')

        if LOGO_MARK_WHITE_PATH.exists():

            st.image(str(LOGO_MARK_WHITE_PATH), width=48)

        elif LOGO_MARK_PATH.exists():

            st.image(str(LOGO_MARK_PATH), width=48)

        elif LOGO_PATH.exists():

            st.image(str(LOGO_PATH), width=48)

        else:

            render_html(
                '<div style="font-size:32px; color:{WHITE}; '
                'line-height:48px;">⚡</div>'
            )

    with col_title:

        render_html(
            '<div class="app-title">AppInSnap Support</div>'
        )

    with col_user:

        if st.session_state.customer_logged_in:

            render_html(
                f'<div class="header-user">{st.session_state.customer_name}</div>'
            )

        elif st.session_state.admin_logged_in:

            render_html(
                f'<div class="header-user">{st.session_state.admin_email}</div>'
            )


show_header()


# =========================================================
# NOT LOGGED IN (neither customer nor admin)
# =========================================================

if not st.session_state.customer_logged_in and not st.session_state.admin_logged_in:

    # =====================================================
    # TOP-LEVEL LANDING MENU: Customer / Admin
    # =====================================================

    if st.session_state.account_view is None:

        if LOGO_PATH.exists():

            spacer_l, logo_col, spacer_r = st.columns([1, 1, 1])

            with logo_col:
                st.image(str(LOGO_PATH), width=220)

        render_html(
            """
            <div class="welcome">
                <h1>Welcome to AppInSnap Support</h1>
                <p>Choose how you'd like to continue.</p>
            </div>
            """
        )

        render_html('<div class="landing-wrap">')

        col_a, col_b = st.columns(2)

        with col_a:

            if st.button(
                "👤   Customer\n\nLogin or create an account to chat with support",
                key="menu_customer",
                use_container_width=True
            ):

                st.session_state.account_view = "customer"

                st.rerun()

        with col_b:

            if st.button(
                "🛠️   Admin / Staff\n\nSign in with your staff email and password",
                key="menu_admin",
                use_container_width=True
            ):

                st.session_state.account_view = "admin"

                st.rerun()

        render_html('</div>')


    # =====================================================
    # CUSTOMER: LOGIN / REGISTER
    # =====================================================

    elif st.session_state.account_view == "customer":

        if st.button("← Back", key="back_from_customer"):

            st.session_state.account_view = None

            st.rerun()

        render_html(
            """
            <div class="account-title">Customer Account</div>
            <div class="account-subtitle">
                Login or create an account to chat with AppInSnap Support
            </div>
            """
        )

        login_tab, register_tab = st.tabs(["Login", "Register"])

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        with login_tab:

            with st.form("customer_login"):

                email = st.text_input("Email")

                password = st.text_input("Password", type="password")

                login = st.form_submit_button(
                    "Login",
                    use_container_width=True
                )

            if login:

                if not email.strip():

                    st.error("Please enter your email.")

                elif not password:

                    st.error("Please enter your password.")

                else:

                    result = login_customer(email.strip(), password)

                    if result.get("success"):

                        st.session_state.customer_logged_in = True
                        st.session_state.customer_email = result.get("email", email.strip())
                        st.session_state.customer_user_id = result.get("localId", "")
                        st.session_state.id_token = result.get("idToken", "")
                        st.session_state.customer_name = email.split("@")[0]
                        st.session_state.messages = []
                        st.session_state.waiting_for_complaint = False
                        st.session_state.complaint_prompt_sent = False
                        st.session_state.account_view = None

                        st.rerun()

                    else:

                        st.error(result.get("error", "Login failed."))

        # -------------------------------------------------
        # REGISTER
        # -------------------------------------------------

        with register_tab:

            with st.form("customer_register"):

                name = st.text_input("Full Name")

                reg_email = st.text_input("Email", key="reg_email")

                reg_password = st.text_input(
                    "Password", type="password", key="reg_password"
                )

                confirm_password = st.text_input(
                    "Confirm Password", type="password"
                )

                submit = st.form_submit_button(
                    "Create Account",
                    use_container_width=True
                )

            if submit:

                if not name.strip():

                    st.error("Please enter your name.")

                elif not reg_email.strip():

                    st.error("Please enter your email.")

                elif len(reg_password) < 6:

                    st.error("Password must contain at least 6 characters.")

                elif reg_password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    result = register_customer(
                        name.strip(), reg_email.strip(), reg_password
                    )

                    if result.get("success"):

                        st.session_state.customer_logged_in = True
                        st.session_state.customer_name = name.strip()
                        st.session_state.customer_email = reg_email.strip()
                        st.session_state.customer_user_id = result.get("localId", "")
                        st.session_state.id_token = result.get("idToken", "")
                        st.session_state.messages = []
                        st.session_state.waiting_for_complaint = False
                        st.session_state.complaint_prompt_sent = False
                        st.session_state.account_view = None

                        st.rerun()

                    else:

                        st.error(result.get("error", "Registration failed."))


    # =====================================================
    # ADMIN LOGIN
    # =====================================================

    elif st.session_state.account_view == "admin":

        if st.button("← Back", key="back_from_admin"):

            st.session_state.account_view = None

            st.rerun()

        render_html(
            """
            <div class="account-title">Staff / Admin</div>
            <div class="account-subtitle">Authorized staff only</div>
            """
        )

        with st.form("admin_login"):

            admin_email = st.text_input("Admin Email")

            admin_password = st.text_input("Admin Password", type="password")

            admin_login = st.form_submit_button(
                "Admin Login",
                use_container_width=True
            )

        if admin_login:

            if not admin_email.strip():

                st.error("Please enter your admin email.")

            elif not admin_password:

                st.error("Please enter your admin password.")

            else:

                result = login_firebase_user(admin_email.strip(), admin_password)

                if not result.get("success"):

                    st.error(result.get("error", "Admin login failed."))

                else:

                    user_id = result.get("localId", "")

                    if is_admin(user_id):

                        st.session_state.admin_logged_in = True
                        st.session_state.admin_user_id = user_id
                        st.session_state.admin_email = result.get("email", admin_email.strip())
                        st.session_state.admin_id_token = result.get("idToken", "")
                        st.session_state.account_view = None

                        st.rerun()

                    else:

                        st.error("This account does not have admin access.")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

elif st.session_state.admin_logged_in:

    # Same logo + title treatment as the customer sidebar, so both
    # sidebars are visually consistent (same logo size, same title
    # font size/weight/length).
    admin_sidebar_logo = LOGO_MARK_PATH if LOGO_MARK_PATH.exists() else LOGO_PATH

    if admin_sidebar_logo.exists():

        admin_logo_col, admin_title_col = st.sidebar.columns([0.22, 0.78])

        with admin_logo_col:
            st.image(str(admin_sidebar_logo), width=40)

        with admin_title_col:
            st.markdown(
                f'<div style="font-size:20px; font-weight:700; '
                f'color:{ACCENT_DARK}; margin-top:6px;">AppInSnap</div>',
                unsafe_allow_html=True
            )

    else:

        st.sidebar.markdown("## 🛠️ AppInSnap")

    st.sidebar.markdown(
        f'<div style="color:{ACCENT}; font-size:14px; font-weight:700; '
        f'margin-top:6px; margin-bottom:10px;">🛠️ Admin</div>',
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        f"""
        <div style="
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 18px;
        ">
            <div style="color: {MUTED}; font-size: 13px;">
                Logged in as
            </div>
            <div style="color: {TEXT}; font-size: 16px; font-weight: 600; margin-top: 4px; word-break: break-all;">
                {st.session_state.admin_email}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.sidebar.button("🚪  Logout Admin", use_container_width=True, key="admin_logout"):

        st.session_state.admin_logged_in = False
        st.session_state.admin_user_id = ""
        st.session_state.admin_email = ""
        st.session_state.admin_id_token = ""
        st.session_state.account_view = None

        st.rerun()

    st.sidebar.markdown("---")

    # admin_dashboard() is expected to render its own internal
    # navigation, including the complaint list + status-update view.
    # See admin/admin_dashboard.py for that page.
    admin_dashboard()


# =========================================================
# CUSTOMER LOGGED IN
# =========================================================

else:

    # =====================================================
    # CUSTOMER SIDEBAR
    # =====================================================

    sidebar_logo = LOGO_MARK_PATH if LOGO_MARK_PATH.exists() else LOGO_PATH

    if sidebar_logo.exists():

        logo_col, title_col = st.sidebar.columns([0.22, 0.78])

        with logo_col:
            st.image(str(sidebar_logo), width=40)

        with title_col:
            st.markdown(
                f'<div style="font-size:20px; font-weight:700; '
                f'color:{ACCENT_DARK}; margin-top:6px;">AppInSnap</div>',
                unsafe_allow_html=True
            )

    else:

        st.sidebar.markdown("## ⚡ AppInSnap")

    st.sidebar.markdown(
        f"""
        <div style="
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 14px;
            margin-top: 14px;
            margin-bottom: 18px;
        ">
            <div style="color: {MUTED}; font-size: 13px;">
                Logged in as
            </div>
            <div style="color: {TEXT}; font-size: 16px; font-weight: 600; margin-top: 4px;">
                {st.session_state.customer_name}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        f"""
        <div style="color: {ACCENT}; font-size: 14px; font-weight: 700; margin-bottom: 8px;">
            Customer Menu
        </div>
        """,
        unsafe_allow_html=True
    )

    # Only two customer-facing pages. There is intentionally no
    # standalone "Register Complaint" page — complaints can only be
    # filed by chatting with support (see the Chat Support flow below).
    page = st.sidebar.radio(
        "Customer Menu",
        ["Chat Support", "Check Status"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪  Logout", use_container_width=True, key="customer_logout"):

        st.session_state.customer_logged_in = False
        st.session_state.customer_name = ""
        st.session_state.customer_email = ""
        st.session_state.customer_user_id = ""
        st.session_state.id_token = ""
        st.session_state.messages = []
        st.session_state.waiting_for_complaint = False
        st.session_state.complaint_prompt_sent = False
        st.session_state.account_view = None

        st.rerun()

    if page == "Chat Support":

        chat_mode = True

        if not st.session_state.waiting_for_complaint:

            st.session_state.complaint_prompt_sent = False

    else:

        chat_mode = False


    # =====================================================
    # CHAT SUPPORT
    # =====================================================

    if chat_mode:

        if not st.session_state.messages:

            render_html(
                """
                <div class="welcome">
                    <h1>How can we help you?</h1>
                    <p>Ask anything about AppInSnap or report a problem.</p>
                </div>
                """
            )

            if st.button(
                "💬   I want to ask about AppInSnap",
                key="suggestion_ask",
                use_container_width=True
            ):

                question = "I want to ask about AppInSnap"

                st.session_state.messages.append(
                    {"role": "user", "content": question}
                )

                with st.chat_message("user"):

                    st.markdown(question)

                with st.chat_message("assistant"):

                    with st.spinner("Searching the AppInSnap knowledge base..."):

                        answer = strip_bold(answer_question(question))

                    st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

                st.rerun()

            if st.button(
                "⚠️   I want to report a problem",
                key="suggestion_problem",
                use_container_width=True
            ):

                st.session_state.waiting_for_complaint = True

                message = (
                    "I'm sorry you're experiencing a problem. "
                    "I can help you register a complaint.\n\n"
                    "Please describe your problem in detail."
                )

                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )

                st.rerun()

            if st.button(
                "📝   I want to register a complaint",
                key="suggestion_complaint",
                use_container_width=True
            ):

                st.session_state.waiting_for_complaint = True

                message = (
                    "Sure, I can help you register a complaint. 📝\n\n"
                    "Please describe your problem in detail."
                )

                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )

                st.rerun()


        # -------------------------------------------------
        # CHAT HISTORY
        # -------------------------------------------------

        for message in st.session_state.messages:

            with st.chat_message(message["role"]):

                if message.get("is_html"):

                    render_html(message["content"])

                else:

                    st.markdown(message["content"])


        # -------------------------------------------------
        # CHAT INPUT
        # -------------------------------------------------

        question = st.chat_input("Message AppInSnap Support...")

        if question:

            question = question.strip()

            if not question:

                st.stop()

            st.session_state.messages.append(
                {"role": "user", "content": question}
            )

            with st.chat_message("user"):

                st.markdown(question)

            # ===============================================
            # COMPLAINT DETAILS (only entry point for filing one)
            # ===============================================

            if st.session_state.waiting_for_complaint:

                try:

                    complaint_id = register_complaint(
                        st.session_state.customer_name,
                        question,
                        st.session_state.customer_email,
                        st.session_state.customer_user_id
                    )

                    st.session_state.waiting_for_complaint = False
                    st.session_state.complaint_prompt_sent = False

                    card_html = build_complaint_card_html(
                        complaint_id,
                        question,
                        "Pending",
                        st.session_state.customer_name
                    )

                    with st.chat_message("assistant"):

                        render_html(card_html)

                        st.caption(
                            "You can check its status anytime from Check Status."
                        )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": card_html,
                            "is_html": True
                        }
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "You can check its status anytime from Check Status.",
                        }
                    )

                except Exception as e:

                    response = f"Unable to register complaint: {e}"

                    with st.chat_message("assistant"):

                        st.error(response)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

            # ===============================================
            # NEW COMPLAINT DETECTION
            # ===============================================

            elif is_complaint(question):

                st.session_state.waiting_for_complaint = True
                st.session_state.complaint_prompt_sent = True

                response = (
                    "I'm sorry you're experiencing a problem. "
                    "I can help you register a complaint.\n\n"
                    "Please describe your complaint in detail."
                )

                with st.chat_message("assistant"):

                    st.markdown(response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            # ===============================================
            # NORMAL RAG — scoped to AppInSnap only.
            #
            # The raw question is sent as-is. Scoping is enforced
            # inside agents/support_agent.py (system prompt + a hard
            # retrieval-confidence gate), NOT by prepending instruction
            # text here. Prepending instructions to the question used
            # to corrupt the retrieval step, because that whole block
            # of text (not just the question) was being embedded and
            # searched against the knowledge base — which is what let
            # off-topic questions like "define physics" slip through
            # and get answered instead of refused.
            # ===============================================

            else:

                with st.chat_message("assistant"):

                    with st.spinner("Searching the AppInSnap knowledge base..."):

                        answer = strip_bold(answer_question(question))

                    st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )


    # =====================================================
    # CHECK STATUS
    # =====================================================

    elif page == "Check Status":

        render_html(
            """
            <div class="welcome">
                <h1>Complaint Status</h1>
                <p>View the complaints registered under your account.</p>
            </div>
            """
        )

        try:

            complaints = get_customer_complaints(
                st.session_state.customer_user_id
            )

        except Exception as e:

            st.error(f"Unable to load your complaints: {e}")

            complaints = []

        if not complaints:

            render_html(
                f"""
                <div style="
                    background: {CARD};
                    border: 1px solid {BORDER};
                    border-radius: 16px;
                    padding: 25px;
                    text-align: center;
                    color: {MUTED};
                ">
                    You have not registered any complaints yet.
                </div>
                """
            )

        else:

            for complaint in complaints:

                complaint_id = complaint.get("complaint_id", "")
                complaint_text = complaint.get("complaint", "")
                status = complaint.get("status", "Pending")

                if status == "Resolved":

                    status_color = GREEN

                elif status == "In Progress":

                    status_color = ACCENT

                else:

                    status_color = YELLOW

                render_html(
                    f"""
                    <div class="complaint-card">
                        <div class="complaint-id">
                            Complaint ID:
                            <span style="color:{TEXT};">{complaint_id}</span>
                        </div>
                        <div class="complaint-description">
                            {complaint_text}
                        </div>
                        <div class="complaint-status">
                            Status:
                            <span style="color:{status_color}; font-weight:700;">
                                {status}
                            </span>
                        </div>
                    </div>
                    """
                )