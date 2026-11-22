# Codex project brief — IEEE emergency department study reproduction + original extension

## Source and attribution
Jun Wang and Jiacun Wang, "Real-Time Adaptive Allocation of Emergency Department Resources and Performance Simulation Based on Stochastic Timed Petri Nets," IEEE Transactions on Computational Social Systems 10(4), 2023. DOI 10.1109/TCSS.2023.3266501.
Use the user-supplied paper as the source. Never claim this repo is the authors' released source code.

## Goal
1. Recreate the major experiments for emergency department (ED) patient flow with 4 triage branches.
2. Compare no backup staff, fixed-threshold observation-response block (ORB), and a proposed severity-and-wait-aware ORB.
3. Build a demo that plots mean/p95 waiting, queue lengths, and backup staffing usage.
4. Demonstrate basic Petri net semantics (places, transitions, tokens, enabled/firing rules) beyond just using a queue simulator.

## Faithfulness ledger
**Paper parameters** (Table II, Fig. 17, Sec IV): 100 patients; grade probabilities 10/15/30/45%; initial staff 4/3/2/2; backups 3/2/1/1; interarrival exponential with example mean 5 min; registration uniform 2–4 min; triage exponential mean 5 min; treatment exponential mean 10 min; ORB queue count >5 (example); transfer and release delays may be uniform 3–10 min in the paper.
**Simplifications in current repo:** registration and triage are independent delays, no staff/resources consumed; only treatment doctor is an exclusive resource; no complete STPN state graph, no condition/inhibitor arcs as an explicit net; transfer/release of backups instantaneous; emergency outcomes and equipment omitted; target time thresholds in code are hypotheses, not medical advice. These changes prevent exact Table IV replication. Explicitly retain these caveats.

## Existing files
`src/simulation.py`: stochastic demand, doctor tokens, policies.
`src/experiment.py`: repeated paired random seeds, CSV and plot.
`app.py`: Streamlit demo.
`main.py`: CLI.
`tests/test_simulation.py`: determinism, conservation, staffing limits.

## Project extension
The published ORB uses a queue threshold (>5) to activate backup doctors. Proposed Adaptive Priority-Aware ORB (APA-ORB):
- estimate queued workload `queue_length * mean_service_time / active_doctors`;
- combine it with `oldest_wait` normalized by a configurable grade-specific target;
- activate one available backup doctor per polling cycle when `pressure >= trigger`;
- respect the backup limits; never remove a doctor while treating a patient;
- release backups when queue is empty. Consider hysteresis/cooldown to prevent oscillation.
No patient-care decision or triage scoring is claimed to be clinically validated.

## Milestones and acceptance criteria
### M1 — environment and sanity checks
Install dependencies; execute `pytest -q` and `python main.py`. Confirm outputs exist. Fix any failing behavior before adding functionality.
### M2 — visualization
Launch Streamlit. Add time-series queue charts for all grades and policies; display active doctors over time. Ensure axis units and meanings are clear.
### M3 — STPN fidelity
Create `src/petri_net.py` with Place, Transition, Arc, Token, enabled and fire methods. Model treatment queue and doctor pool with resource-token conservation. Add test for invariant: each grade's total doctor tokens across idle+busy = base + currently active backups. Model enabled transition and consumption/production explicitly. Explain any behavior abstracted through SimPy.
### M4 — original behavior
Implement configurable delay for transferring backup doctors; implement return policy; model resource-constrained registration and triage; use reference figure top-level workflow including four grade branches. Keep exact paper parameters in a config file and annotate unknowns. Check paper tables, do not invent empirical inputs.
### M5 — evaluate improvement fairly
Use identical pre-sampled patient traces per policy, >=30 seeds per condition. Sweep mean interarrival times [1,2,5,10,20] minutes and report per-grade means, p95, deadline violations, max queue, backup-doctor minutes, ORB trigger counts and 95% CI. Plot results and show cases where new policy does NOT improve. Add sensitivity to trigger thresholds. Do not equate a simulation demo with a validated clinical system.
### M6 — report
Write a report with: original paper summary, mathematical model, implementation architecture, faithfulness differences, extension hypothesis, experiment protocol, quantitative results, limitations, and references. Save reproducible commands and seeds.

## Concrete implementation instructions
- Maintain small readable Python modules, type hints, unit tests, and explicit config.
- Keep three policy modes `baseline`, `orb`, `improved` unchanged for fair comparison.
- Do not overwrite paper results with our outputs; label them separately.
- All workflows must run on a MacBook Air M1 with CPU and no paid APIs.
- Code should be understandable for an M.Tech student to explain in a viva.
- First inspect current files and run tests. Fix tests before implementation. Work incrementally, one milestone at a time, stating which file and why.

## Demo criteria
User can change patient count and mean interarrival, execute 3 policies, see wait-time comparison, p95, staffing activations, grade-specific results, export CSV and show trace of a single synthetic patient's route.
