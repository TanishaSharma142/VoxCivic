import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "pages") not in sys.path:
    sys.path.insert(0, str(ROOT / "pages"))

st.set_page_config(page_title="VoxCivic", page_icon="🏛️", layout="wide")

st.sidebar.title("VoxCivic")
page = st.sidebar.radio("Navigate", ["Submit Complaint", "Officer Dashboard", "AI Chat"])

if page == "Submit Complaint":
    from submit_complaint import show
    show()
elif page == "Officer Dashboard":
    from dashboard import show
    show()
elif page == "AI Chat":
    from ai_chat import show
    show()