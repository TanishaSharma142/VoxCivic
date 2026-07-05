import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_priorities, run_analytics


def show():
    st.title("📊 Municipal Officer Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Open Complaints", "12")
    col2.metric("High Severity", "3")
    col3.metric("Duplicate Flags", "2")

    st.subheader("📈 Trend Analysis")
    if st.button("Run Analytics (GPU Accelerated)"):
        with st.spinner("Running NVIDIA RAPIDS analytics..."):
            analytics = run_analytics()
            if 'summary' in analytics:
                st.info(analytics['summary'])
                if 'pivot' in analytics and analytics['pivot']:
                    pivot_df = pd.DataFrame(analytics['pivot'])
                    if not pivot_df.empty:
                        pivot_table = pivot_df.pivot_table(index='location_ward', columns='category', values='count', fill_value=0)
                        fig = px.imshow(pivot_table, text_auto=True, aspect="auto", title="Complaints by Ward & Category")
                        st.plotly_chart(fig, use_container_width=True)
                if analytics.get('spike_dates'):
                    st.error(f"⚠️ Severity spikes detected on: {', '.join(analytics['spike_dates'])}")
            else:
                st.warning("No analytics data yet. If the backend is not running, start it with uvicorn backend.main:app.")

    st.subheader("🚨 Priority Recommendations")
    if st.button("Get AI Priorities"):
        priorities = get_priorities()
        if 'priorities' in priorities:
            for idx, p in enumerate(priorities['priorities'], 1):
                st.markdown(f"**{idx}. {p.get('issue', 'N/A')}**")
                st.caption(f"Ward: {p.get('ward', '?')} | Dept: {p.get('department', '?')}")
                st.write(p.get('action', ''))
                if p.get('reason'):
                    st.write(f"*Reason:* {p['reason']}")
                st.divider()
        else:
            st.write(priorities.get('raw', 'No priorities returned.'))