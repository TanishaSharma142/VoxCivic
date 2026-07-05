import streamlit as st
from utils import ask_question

def show():
    st.title("💬 Ask VoxCivic")
    st.markdown("Ask questions like *'What should we prioritize today?'* or *'Which ward has the most sanitation issues?'*")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Thinking..."):
            response = ask_question(prompt)
            answer = response.get("answer", "I'm unable to process that right now.")
        with st.chat_message("assistant"):
            st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})