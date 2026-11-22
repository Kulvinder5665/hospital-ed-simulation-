import streamlit as st
import pandas as pd
from src.simulation import run_simulation

st.set_page_config(page_title="ED Resource Allocation", layout="wide")
st.title("Emergency Department Resource Allocation Simulator")
st.caption("Research prototype using synthetic patients; not a clinical decision system")
n = st.slider("Number of patients", 20, 500, 100, 20)
arrival = st.slider("Mean arrival interval (minutes)", 1.0, 30.0, 5.0)
seed = st.number_input("Random seed", min_value=0, value=42)
settings = (n, arrival, int(seed))
if st.button("Compare policies", type="primary"):
    summaries, frames = [], {}
    for policy in ("baseline", "orb", "improved"):
        data, _, summary = run_simulation(policy, *settings)
        summaries.append(summary)
        frames[policy] = data
    st.session_state.comparison = (
        settings,
        pd.DataFrame(summaries),
        pd.concat([df.assign(policy=name) for name, df in frames.items()]),
    )

comparison = st.session_state.get("comparison")
if comparison is not None and comparison[0] == settings:
    _, report, grade_stats = comparison
    st.subheader("Comparison")
    st.dataframe(report)
    st.bar_chart(report.set_index("policy")["mean_queue_wait"])
    st.subheader("Waiting time by triage grade")
    chart = grade_stats.groupby(["policy", "grade"])["treatment_queue_wait"].mean().unstack(0)
    st.bar_chart(chart)
    st.download_button("Download patient data (CSV)", grade_stats.to_csv(index=False),
                       "patient_comparison.csv", "text/csv")
