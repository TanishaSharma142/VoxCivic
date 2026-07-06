import streamlit as st


def render_priority_table(rows: list[dict]):
    st.table(rows)
