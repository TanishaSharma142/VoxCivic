import streamlit as st
import pandas as pd


def render_bar_chart(data: list[dict], x: str, y: str, title: str):
    df = pd.DataFrame(data)
    st.bar_chart(df.set_index(x)[y])


def render_line_chart(data: list[dict], x: str, y: str, title: str):
    df = pd.DataFrame(data)
    st.line_chart(df.set_index(x)[y])
