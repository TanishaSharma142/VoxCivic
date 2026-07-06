import streamlit as st
from frontend.utils.api_client import ask_chat


def main():
    st.header("AI Chat")
    question = st.text_input("Ask a question about civic complaints")
    if st.button("Ask") and question:
        response = ask_chat(question)
        if response.get("success"):
            payload = response.get("payload", {})
            st.write(payload.get("answer"))
            if payload.get("records"):
                st.write(payload.get("records"))
        else:
            st.error(response.get("message", "Chat request failed"))
