import streamlit as st

from data.complaints import (
    get_all_complaints,
    get_complaint,
    update_complaint_status
)


STATUS_OPTIONS = ["Pending", "In Progress", "Resolved"]

ACCENT = "#4F35E0"
ACCENT_DARK = "#3820B8"
ACCENT_SOFT = "#EEEBFF"
TEXT = "#1A162A"
MUTED = "#6B7787"
BORDER = "#E7E4F2"

GREEN = "#16A34A"
GREEN_SOFT = "#E9F9EF"
YELLOW = "#D97706"
YELLOW_SOFT = "#FEF3E2"
TEAL = "#12B8A6"
TEAL_SOFT = "#E4FBF7"

STATUS_COLORS = {
    "Pending": (YELLOW, YELLOW_SOFT),
    "In Progress": (TEAL, TEAL_SOFT),
    "Resolved": (GREEN, GREEN_SOFT),
}


def _status_badge(status):

    color, soft = STATUS_COLORS.get(status, (MUTED, "#F1F1F5"))

    return (
        f'<span style="'
        f'display:inline-block; padding:3px 12px; border-radius:999px; '
        f'background:{soft}; color:{color}; font-size:12px; '
        f'font-weight:700; letter-spacing:0.2px;">{status}</span>'
    )


def _render_status_updater(complaint, key_prefix):
    """
    Shared block: customer/complaint details + a status dropdown
    and Update button. Used both by the lookup-by-ID card and by
    each row in the full complaint list.
    """

    complaint_id = complaint.get("complaint_id", "")
    complaint_text = complaint.get("complaint", "")
    customer_name = complaint.get("name", complaint.get("customer_name", ""))
    customer_email = complaint.get("email", "")
    current_status = complaint.get("status", "Pending")
    status_color, _ = STATUS_COLORS.get(current_status, (MUTED, "#F1F1F5"))

    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border:1px solid {BORDER};
            border-left:4px solid {status_color};
            border-radius:12px;
            padding:18px 20px 4px 20px;
            margin-bottom:14px;
            box-shadow:0 1px 3px rgba(26,22,42,0.05);
        ">
        """,
        unsafe_allow_html=True
    )

    top_col, badge_col = st.columns([0.75, 0.25])

    with top_col:

        st.markdown(
            f"**Complaint ID:** `{complaint_id}`  \n"
            f"**Customer:** {customer_name} ({customer_email})"
        )

    with badge_col:

        st.markdown(
            f'<div style="text-align:right; margin-top:4px;">'
            f'{_status_badge(current_status)}</div>',
            unsafe_allow_html=True
        )

    st.write(complaint_text)

    status_col, button_col = st.columns([0.6, 0.4])

    with status_col:

        new_status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(current_status)
            if current_status in STATUS_OPTIONS else 0,
            key=f"{key_prefix}_status_select_{complaint_id}",
            label_visibility="collapsed"
        )

    with button_col:

        if st.button(
            "Update",
            key=f"{key_prefix}_update_btn_{complaint_id}",
            use_container_width=True
        ):

            try:

                update_complaint_status(complaint_id, new_status)

                st.success(f"Complaint {complaint_id} updated to '{new_status}'.")

                st.rerun()

            except Exception as e:

                st.error(f"Failed to update complaint: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


def _stat_card(label, value, color, soft):

    st.markdown(
        f"""
        <div style="
            background:{soft};
            border:1px solid {BORDER};
            border-radius:14px;
            padding:16px 18px;
            text-align:center;
        ">
            <div style="color:{color}; font-size:28px; font-weight:800;">
                {value}
            </div>
            <div style="color:{TEXT}; font-size:13px; font-weight:600; margin-top:2px;">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def admin_dashboard():
    """
    Renders the admin dashboard:
      1. Look up a single complaint by ID and update its status.
      2. Browse/filter the full complaint list — only once an admin
         has actually searched, so complaint details aren't exposed
         on page load.

    Requires these functions in data/complaints.py:
      - get_all_complaints() -> list[dict]
      - get_complaint(complaint_id) -> dict | None
      - update_complaint_status(complaint_id, new_status) -> None
    """

    st.markdown(
        f"""
        <div style="
            text-align:center;
            margin-top:4px;
            margin-bottom:26px;
        ">
            <h1 style="color:{ACCENT_DARK}; font-size:32px; font-weight:700;">
                Complaints
            </h1>
            <p style="color:{MUTED}; font-size:16px;">
                Review and update the status of any customer's complaint &mdash; any admin can change the status of any complaint, for any user.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------
    # LOAD DATA UP FRONT — used by both the stat row and
    # the full list further down.
    # ---------------------------------------------------

    try:

        all_complaints = get_all_complaints()

    except Exception as e:

        all_complaints = []

        st.error(f"Unable to load complaints: {e}")

    # ---------------------------------------------------
    # STAT SUMMARY ROW
    # ---------------------------------------------------

    if all_complaints:

        total = len(all_complaints)
        pending = sum(1 for c in all_complaints if c.get("status", "Pending") == "Pending")
        in_progress = sum(1 for c in all_complaints if c.get("status") == "In Progress")
        resolved = sum(1 for c in all_complaints if c.get("status") == "Resolved")

        s1, s2, s3, s4 = st.columns(4)

        with s1:
            _stat_card("Total", total, ACCENT_DARK, ACCENT_SOFT)

        with s2:
            _stat_card("Pending", pending, YELLOW, YELLOW_SOFT)

        with s3:
            _stat_card("In Progress", in_progress, TEAL, TEAL_SOFT)

        with s4:
            _stat_card("Resolved", resolved, GREEN, GREEN_SOFT)

        st.write("")

    # ---------------------------------------------------
    # LOOK UP A SINGLE COMPLAINT BY ID
    # ---------------------------------------------------

    with st.container(border=True):

        st.markdown("#### 🔍 Look up a complaint")

        lookup_col, btn_col = st.columns([0.7, 0.3])

        with lookup_col:

            lookup_id = st.text_input(
                "Complaint ID",
                placeholder="e.g. CMP-6B9C0D77",
                label_visibility="collapsed"
            )

        with btn_col:

            find_clicked = st.button(
                "Find", use_container_width=True, type="primary"
            )

        if find_clicked:

            st.session_state["admin_has_searched"] = True

            if not lookup_id.strip():

                st.warning("Enter a complaint ID first.")

            else:

                try:

                    found = get_complaint(lookup_id.strip())

                except Exception as e:

                    found = None

                    st.error(f"Unable to look up complaint: {e}")

                if found:

                    st.write("")

                    _render_status_updater(found, key_prefix="lookup")

                else:

                    st.warning(f"No complaint found with ID '{lookup_id.strip()}'.")

    # ---------------------------------------------------
    # FULL LIST — deliberately hidden until an admin has
    # actually searched for a complaint, so the full list
    # of customer complaints isn't exposed just by opening
    # this page.
    # ---------------------------------------------------

    if not st.session_state.get("admin_has_searched"):

        return

    st.write("")

    st.markdown("#### 📋 All complaints")

    if not all_complaints:

        st.info("No complaints have been registered yet.")

        return

    complaints = all_complaints

    filter_col, _ = st.columns([0.3, 0.7])

    with filter_col:

        status_filter = st.selectbox(
            "Filter by status",
            ["All"] + STATUS_OPTIONS
        )

    if status_filter != "All":

        complaints = [
            c for c in complaints
            if c.get("status", "Pending") == status_filter
        ]

    if not complaints:

        st.info(f"No complaints with status '{status_filter}'.")

        return

    for complaint in complaints:

        _render_status_updater(complaint, key_prefix="list")