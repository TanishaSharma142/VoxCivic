import streamlit as st
import requests
from PIL import Image
import io

from utils import API_BASE


def show():
    st.set_page_config(page_title="Submit Complaint", page_icon="📝")
    st.title("📢 Report a Civic Issue")

    with st.form("complaint_form"):
        text = st.text_area(
            "Describe the issue *",
            height=150,
            placeholder="E.g., Large pothole near main road, water leaking from pipe...",
        )
        ward = st.text_input("Ward / Area (optional)", placeholder="Ward 12")
        contact = st.text_input("Your contact (optional, for follow-up)", placeholder="Phone or email")
        image_file = st.file_uploader("Upload a photo (optional)", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Submit Complaint")

    if submit:
        if not text or len(text) < 10:
            st.error("Please provide a detailed description (min 10 characters).")
        else:
            with st.spinner("Processing your complaint with AI..."):
                files = {}
                data = {
                    "text": text,
                    "location_ward": ward or None,
                    "citizen_contact": contact or None,
                }
                if image_file is not None:
                    img_bytes = image_file.read()
                    files["image"] = (image_file.name, img_bytes, image_file.type)

                try:
                    response = requests.post(
                        f"{API_BASE}/submit-complaint",
                        data=data,
                        files=files,
                        timeout=30,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Complaint registered successfully!")
                        st.json(result)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to backend: {e}")