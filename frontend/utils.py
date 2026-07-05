import os
import requests
import streamlit as st
from typing import Optional, Dict

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def submit_complaint(
    text: str,
    ward: str,
    contact: str,
    image_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None
) -> Dict:
    files = {}
    data = {"text": text, "location_ward": ward, "citizen_contact": contact}
    if image_file is not None:
        image_bytes = image_file.read()
        files["image"] = (image_file.name, image_bytes, image_file.type)
    resp = requests.post(f"{API_BASE}/submit-complaint", data=data, files=files)
    return resp.json()

def run_analytics():
    resp = requests.get(f"{API_BASE}/analytics/run")
    return resp.json()

def get_priorities():
    resp = requests.get(f"{API_BASE}/decision/priorities")
    return resp.json()

def generate_work_order(complaint_id: str):
    resp = requests.post(f"{API_BASE}/communication/work-order?complaint_id={complaint_id}")
    return resp.json()

def ask_question(query: str):
    resp = requests.post(f"{API_BASE}/communication/chat", json={"query": query})
    return resp.json()