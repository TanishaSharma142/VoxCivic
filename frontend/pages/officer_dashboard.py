import streamlit as st
from frontend.utils.api_client import get_priority_queue


def main():
    st.header("Officer Dashboard")
    st.subheader("Priority Queue")
    response = get_priority_queue()
    if response.get("success"):
        rows = response.get("payload", [])
        st.write(rows)
    else:
        st.error(response.get("message", "Could not load priority queue"))
