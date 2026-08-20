import streamlit as st

from data.complaints import (
    get_all_complaints,
    get_complaint,
    update_complaint_status
)


STATUS_OPTIONS = ["Pending", "In Progress", "Resolved"]


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

    with st.container(border=True):

        st.markdown(
            f"**Complaint ID:** `{complaint_id}`  \n"
            f"**Customer:** {customer_name} ({customer_email})"
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


def admin_dashboard():
    """
    Renders the admin dashboard:
      1. Look up a single complaint by ID and update its status.
      2. Browse/filter the full complaint list, each with its own
         status dropdown + Update button.

    Requires these functions in data/complaints.py:
      - get_all_complaints() -> list[dict]
      - get_complaint(complaint_id) -> dict | None
      - update_complaint_status(complaint_id, new_status) -> None
    """

    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:10px;
            margin-bottom:30px;
        ">
            <h1 style="color:#1A2233; font-size:32px; font-weight:700;">
                Complaints
            </h1>
            <p style="color:#6B7787; font-size:15px;">
                Review and update the status of customer complaints.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------
    # LOOK UP A SINGLE COMPLAINT BY ID
    # ---------------------------------------------------

    st.markdown("#### Look up a complaint")

    lookup_col, btn_col = st.columns([0.7, 0.3])

    with lookup_col:

        lookup_id = st.text_input(
            "Complaint ID",
            placeholder="e.g. CMP-6B9C0D77",
            label_visibility="collapsed"
        )

    with btn_col:

        find_clicked = st.button("Find", use_container_width=True)

    if find_clicked:

        if not lookup_id.strip():

            st.warning("Enter a complaint ID first.")

        else:

            try:

                found = get_complaint(lookup_id.strip())

            except Exception as e:

                found = None

                st.error(f"Unable to look up complaint: {e}")

            if found:

                _render_status_updater(found, key_prefix="lookup")

            else:

                st.warning(f"No complaint found with ID '{lookup_id.strip()}'.")

    st.markdown("---")

    # ---------------------------------------------------
    # FULL LIST
    # ---------------------------------------------------

    st.markdown("#### All complaints")

    try:

        complaints = get_all_complaints()

    except Exception as e:

        st.error(f"Unable to load complaints: {e}")

        return

    if not complaints:

        st.info("No complaints have been registered yet.")

        return

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