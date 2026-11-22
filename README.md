# Emergency Department Resource Allocation Simulation

Educational reproduction/extension inspired by Wang & Wang (2023), DOI: 10.1109/TCSS.2023.3266501.

**Important:** A simplified resource-token discrete-event approximation of the paper, **not** its original full STPN implementation. It currently omits resource-constrained registration/triage, all detailed examination pathways, Petri-net reachability verification, and clinical calibration.

## Run on macOS / VS Code
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python main.py --repetitions 20 --patients 100 --arrival 5
python -m streamlit run app.py
```
In VS Code select `.venv/bin/python` via `Python: Select Interpreter`.

## Outputs
- `outputs/summary.csv` averaged policy comparison
- `outputs/all_runs.csv` full repeated experiment data
- `outputs/patients.csv` synthetic patient-level records
- `outputs/waiting_comparison.png` plot

## Experimental controls
Each scenario generates identical patient demand and pre-sampled treatment times across policy variants, using the same random seed. Run multiple seeds to quantify stochastic variability.

## Interpret metrics
- `mean_queue_wait` only measures the wait for a doctor after registration and triage.
- `pre_treatment_time` includes registration, triage, and doctor-queue wait.
- `sojourn_time` includes registration, triage, queue wait, and treatment.
- `deadline_violations` uses assumed grade-specific simulation thresholds; NOT validated clinical rules.

See `docs/CODEX_TASK.md` for development milestones and research protocol.
