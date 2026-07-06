import base64
import re

import streamlit as st

from config.wards import WARDS
from frontend.utils.api_client import submit_complaint


NOT_SURE_OPTION = "Not sure — let VoxCivic detect it"


def _valid_phone(number: str) -> bool:
    # Loose check: 10-digit Indian mobile number, optional +91 prefix.
    return bool(re.fullmatch(r"(\+91[\-\s]?)?[6-9]\d{9}", number.strip()))


def main():
    st.header("Submit a Complaint")
    st.caption(
        "Tell us what's wrong — a photo helps us assess severity faster, "
        "and selecting your ward means we can route it to the right department immediately."
    )

    # Reset flow after a successful submission, so the form doesn't
    # re-show a stale confirmation on the next visit.
    if "last_submission" not in st.session_state:
        st.session_state.last_submission = None

    with st.form("complaint_form", clear_on_submit=False):
        text = st.text_area(
            "Complaint description",
            placeholder="e.g. There is a large pothole causing traffic slowdowns.",
            height=120,
        )

        col1, col2 = st.columns(2)
        with col1:
            # Ward dropdown: still manual, but we’ll pre-select later
            ward_choice = st.selectbox(
                "Ward",
                options=[NOT_SURE_OPTION] + WARDS,
                help="Pick your ward if you know it. If not, the system will try to detect it from your address.",
            )
        with col2:
            address = st.text_input(
                "Street / landmark",
                placeholder="e.g. Near City Hospital, Ward 5",
                help="Enter your address – the system will try to guess your ward.",
            )

        image = st.file_uploader("Upload photo (optional)", type=["png", "jpg", "jpeg"])
        contact_number = st.text_input(
            "Contact number (optional)",
            placeholder="e.g. 98765 43210",
            help="Only for status updates. Leave blank to report anonymously.",
        )
        submitted = st.form_submit_button("Submit Complaint")

    if submitted:
        if not text.strip():
            st.error("Please describe the issue before submitting.")
            return
        if contact_number.strip() and not _valid_phone(contact_number):
            st.error("Invalid phone number. Leave blank for anonymous submission.")
            return

        image_base64 = None
        if image is not None:
            image_base64 = base64.b64encode(image.read()).decode("utf-8")

        # Send address and ward separately – DO NOT merge them
        manual_ward = None if ward_choice == NOT_SURE_OPTION else ward_choice

        response = submit_complaint(
            text=text.strip(),
            address=address.strip() if address else None,
            image_base64=image_base64,
            ward=manual_ward,
            contact_number=contact_number.strip() or None,
        )
        if response.get("success"):
            st.session_state.last_submission = response.get("payload")
        else:
            st.error(response.get("message", "Submission failed. Please try again."))
            return

    # Confirmation block — shown after a successful submit, persists across
    # reruns until the citizen submits another complaint.
    payload = st.session_state.last_submission
    if payload:
        st.success("Complaint submitted successfully.")

        st.markdown(f"**Tracking ID:** `{payload.get('complaint_id')}`")
        st.caption("Save this ID to follow up on your complaint later.")

        detected_col, ward_col = st.columns(2)
        with detected_col:
            st.metric("Detected category", payload.get("category", "—").replace("_", " ").title())
            st.metric("Severity (1–5)", payload.get("severity", "—"))
        with ward_col:
            ward_display = payload.get("ward") or "Pending confirmation"
            st.metric("Ward on record", ward_display)
            if payload.get("status") == "needs_review":
                st.warning(
                    "We couldn't confidently match this to one of our wards. "
                    "An officer will confirm the location shortly."
                )

        with st.expander("Why this severity?"):
            st.write(payload.get("severity_justification", "No justification available."))

        if st.button("Submit another complaint"):
            st.session_state.last_submission = None
            st.rerun()