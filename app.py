import streamlit as st
import pandas as pd
from src.simulation import run_simulation

# Set up the browser page before displaying the simulation controls.
st.set_page_config(page_title="ED Resource Allocation", layout="wide")
st.title("Emergency Department Resource Allocation Simulator")
st.caption("Research prototype using synthetic patients; not a clinical decision system")
n = st.slider("Number of patients", 20, 500, 100, 20)
arrival = st.slider("Mean arrival interval (minutes)", 1.0, 30.0, 5.0)
seed = st.number_input("Random seed", min_value=0, value=42)
# Keep the inputs together so each policy receives the same patient workload.
settings = (n, arrival, int(seed))
if st.button("Compare policies", type="primary"):
    summaries, frames = [], {}
    for policy in ("baseline", "orb", "improved"):
        # The dashboard uses the patient records and summary. The timeline is unused here.
        data, _, summary = run_simulation(policy, *settings)
        summaries.append(summary)
        frames[policy] = data
    # Streamlit reruns this script on interaction, so store the results in the session.
    # Label patient rows by policy before combining them for the chart and CSV.
    st.session_state.comparison = (
        settings,
        pd.DataFrame(summaries),
        pd.concat([df.assign(policy=name) for name, df in frames.items()]),
    )

comparison = st.session_state.get("comparison")
# Show saved results when they match the inputs currently displayed.
if comparison is not None and comparison[0] == settings:
    _, report, grade_stats = comparison
    st.subheader("Comparison")
    st.dataframe(report)
    st.bar_chart(report.set_index("policy")["mean_queue_wait"])
    st.subheader("Waiting time by triage grade")
    # Average waits by grade and policy, then make each policy a chart series.
    chart = grade_stats.groupby(["policy", "grade"])["treatment_queue_wait"].mean().unstack(0)
    st.bar_chart(chart)
    st.download_button("Download patient data (CSV)", grade_stats.to_csv(index=False),
                       "patient_comparison.csv", "text/csv")
