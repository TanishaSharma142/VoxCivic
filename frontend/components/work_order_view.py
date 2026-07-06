import streamlit as st


def render_work_order(work_order: dict):
    st.write("## Work Order")
    for key, value in work_order.items():
        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
