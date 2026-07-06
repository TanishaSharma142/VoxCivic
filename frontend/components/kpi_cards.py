import streamlit as st


def render_kpi_cards(kpis: dict):
    cols = st.columns(len(kpis))
    for col, (label, value) in zip(cols, kpis.items()):
        col.metric(label, value)
