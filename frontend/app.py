import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from config.settings import settings

st.set_page_config(page_title="VoxCivic", layout="wide")

st.title("VoxCivic")

pages = {
    "Submit Complaint": "frontend.pages.submit_complaint",
    "Officer Dashboard": "frontend.pages.officer_dashboard",
    "AI Chat": "frontend.pages.ai_chat",
}

choice = st.sidebar.selectbox("Choose a page", list(pages.keys()))
module_name = pages[choice]
module = __import__(module_name, fromlist=["*"])
module.main()

st.sidebar.markdown(f"Backend: {settings.BACKEND_URL}")
