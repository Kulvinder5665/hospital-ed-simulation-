"""Paired-seed experimental comparison for baseline, paper-like ORB, and proposal."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from .simulation import run_simulation


def run_experiment(repetitions=20, n=100, mean_interarrival=5.0, output_dir="outputs"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    summaries, details = [], []
    for seed in range(repetitions):
        for policy in ("baseline", "orb", "improved"):
            records, _, summary = run_simulation(policy, n=n,
                                                 mean_interarrival=mean_interarrival,
                                                 seed=seed)
            summaries.append(summary)
            records["policy"], records["seed"] = policy, seed
            details.append(records)
    all_runs = pd.DataFrame(summaries)
    patients = pd.concat(details, ignore_index=True)
    averages = all_runs.groupby("policy", as_index=False)[
        ["mean_queue_wait", "p95_queue_wait", "mean_sojourn",
         "deadline_violations", "activations", "max_queue"]].mean()
    all_runs.to_csv(out / "all_runs.csv", index=False)
    patients.to_csv(out / "patients.csv", index=False)
    averages.to_csv(out / "summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(averages.policy, averages.mean_queue_wait)
    ax.set(xlabel="Policy", ylabel="Mean treatment queue wait (minutes)",
           title="Emergency department: resource allocation policies")
    fig.tight_layout()
    fig.savefig(out / "waiting_comparison.png", dpi=150)
    plt.close(fig)
    return averages
