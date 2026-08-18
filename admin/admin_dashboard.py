import streamlit as st

from data.complaints import (
    get_complaint,
    get_all_complaints,
    update_complaint_status
)


def admin_dashboard():

    st.header("Manage Complaints")

    st.caption(
        "Staff can view and update customer complaints."
    )

    # =====================================================
    # STATUS COUNTS
    # =====================================================

    try:

        complaints = get_all_complaints()

    except Exception as e:

        st.error(
            f"Unable to load complaints: {e}"
        )

        return

    pending = 0
    progress = 0
    resolved = 0

    for complaint in complaints:

        status = complaint.get(
            "status",
            "Pending"
        )

        if status == "Pending":

            pending += 1

        elif status == "In Progress":

            progress += 1

        elif status == "Resolved":

            resolved += 1

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Pending",
            pending
        )

    with col2:

        st.metric(
            "In Progress",
            progress
        )

    with col3:

        st.metric(
            "Resolved",
            resolved
        )

    st.markdown("---")

    # =====================================================
    # FIND COMPLAINT
    # =====================================================

    complaint_id = st.text_input(
        "Complaint ID",
        placeholder="CMP-XXXXXXXX"
    )

    if st.button(
        "Find Complaint",
        use_container_width=True
    ):

        if not complaint_id.strip():

            st.warning(
                "Please enter a Complaint ID."
            )

        else:

            complaint = get_complaint(
                complaint_id.strip().upper()
            )

            if complaint:

                st.session_state.admin_complaint = complaint

            else:

                st.session_state.admin_complaint = None

                st.error(
                    "Complaint not found."
                )

    # =====================================================
    # DISPLAY COMPLAINT
    # =====================================================

    complaint = st.session_state.get(
        "admin_complaint"
    )

    if complaint:

        st.markdown(
            "### Complaint Details"
        )

        st.write(
            f"**Complaint ID:** "
            f"`{complaint.get('complaint_id')}`"
        )

        st.write(
            f"**Customer:** "
            f"{complaint.get('name', '')}"
        )

        st.write(
            f"**Email:** "
            f"{complaint.get('email', '')}"
        )

        st.write(
            f"**Complaint:** "
            f"{complaint.get('complaint', '')}"
        )

        current_status = complaint.get(
            "status",
            "Pending"
        )

        if current_status == "Resolved":

            st.success(
                f"Current Status: {current_status}"
            )

        elif current_status == "In Progress":

            st.info(
                f"Current Status: {current_status}"
            )

        else:

            st.warning(
                f"Current Status: {current_status}"
            )

        # =================================================
        # STATUS DROPDOWN
        # =================================================

        statuses = [
            "Pending",
            "In Progress",
            "Resolved"
        ]

        index = statuses.index(
            current_status
        ) if current_status in statuses else 0

        new_status = st.selectbox(
            "Change Status",
            statuses,
            index=index
        )

        # =================================================
        # BLUE BUTTON
        # =================================================

        st.markdown(
            """
            <style>

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

        if st.button(
            "Change Status",
            use_container_width=True
        ):

            complaint_id = complaint.get(
                "complaint_id"
            )

            success = update_complaint_status(
                complaint_id,
                new_status
            )

            if success:

                st.session_state.admin_complaint = (
                    get_complaint(
                        complaint_id
                    )
                )

                st.session_state.status_updated = (
                    new_status
                )

                st.rerun()

            else:

                st.error(
                    "Complaint could not be updated."
                )

    # =====================================================
    # SUCCESS MESSAGE AFTER RERUN
    # =====================================================

    if "status_updated" in st.session_state:

        st.success(
            "✓ Complaint status successfully "
            f"changed to {st.session_state.status_updated}."
        )

        del st.session_state.status_updated