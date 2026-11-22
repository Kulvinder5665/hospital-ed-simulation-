# Hospital Emergency Department Simulation — Complete Project Guide

**Project:** Educational reproduction and extension of Jun Wang and Jiacun Wang, *Real-Time Adaptive Allocation of Emergency Department Resources and Performance Simulation Based on Stochastic Timed Petri Nets*, IEEE Transactions on Computational Social Systems, 2023, DOI: 10.1109/TCSS.2023.3266501.

**Read this first:** The current starter is a **simplified SimPy discrete-event simulation with doctor resource tokens**, not an exact implementation of the paper's full stochastic timed Petri net (STPN). It does not yet reproduce all paper figures or detailed clinical examination pathways. The `improved` policy is an experimental proposal, not a validated medical policy.

## Start here

Open the folder containing `main.py` in a terminal. For a first run, follow this order:

1. Create and activate `.venv` using the commands for your operating system in sections 3–5.
2. Install dependencies, run `python -m pip check`, then run `python -m pytest -q`. The current suite should report **4 passed**.
3. Run one policy with the Python command in section 6. Check the patient trace to see how the timing metrics fit together.
4. Compare all three with `python main.py --repetitions 20 --patients 100 --arrival 5`. Open `outputs/summary.csv` and the PNG chart.
5. Start the dashboard with `python -m streamlit run app.py`. Click **Compare policies** and use **Ctrl+C** in the terminal when finished.

Use `python main.py --help` to see the CLI options. After the first setup, activate the existing environment each time you open a new terminal. The examples use Python 3.13.3 in the verified macOS environment.

## 1. How the files connect

```text
hospital_ed_sim_starter/   <- project root; run commands HERE
├── main.py                     -> command-line entry point (all 3 policies)
├── app.py                      -> Streamlit web dashboard (all 3 policies)
├── pytest.ini                  -> adds the project root to the test import path
├── requirements.txt            -> Python packages
├── README.md                   -> short original instructions
├── .gitignore                  -> ignored/generated files
├── src/
│   ├── __init__.py             -> marks src as a Python package
│   ├── simulation.py           -> patient generator, stations, 3 policies, metrics
│   └── experiment.py           -> repeated experiments, aggregations, CSV, PNG
├── tests/
│   └── test_simulation.py      -> checks basic simulation behavior
├── docs/
│   ├── CODEX_TASK.md           -> research roadmap
│   └── HOSPITAL_SIMULATION_PROJECT_GUIDE.md -> this guide
└── outputs/                    -> generated after running main.py
    ├── summary.csv
    ├── all_runs.csv
    ├── patients.csv
    └── waiting_comparison.png
```

### Import and execution flow

```text
Terminal: python main.py --repetitions 20 --patients 100 --arrival 5
     |
     v
main.py: reads arguments, calls run_experiment(...)
     |
     v
src/experiment.py: loops over random seeds and 3 policies
     |
     v
src/simulation.py: run_simulation(policy, n, mean_interarrival, seed)
     |                 |
     |                 +-- generate_patients() (random arrival & service times)
     |                 +-- GradeStation (grade-specific doctor tokens)
     |                 +-- SimPy treatment service and queue
     |                 +-- policy control loop (baseline / orb / improved)
     |                 +-- returns patient records, timeline, summary
     v
src/experiment.py: averages policy metrics; creates outputs/*.csv and *.png
     |
     v
main.py: prints comparison table

Browser <-- app.py (Streamlit) --> src/simulation.py
                                  (runs each policy ONCE for chosen seed)

Terminal: python -m pytest -q --> tests/test_simulation.py --> src/simulation.py
```

### File-by-file: what code is inside?

| File | Responsibility | Functions/classes to find |
| --- | --- | --- |
| `main.py` | Parses `--repetitions`, `--patients`, `--arrival`; prints averaged comparison | `argparse`, `run_experiment()` call |
| `src/experiment.py` | Runs each seed under baseline, orb and improved; saves CSV/plot | `run_experiment()` |
| `src/simulation.py` | Entire current simulation logic | `Patient`, `generate_patients()`, `GradeStation`, `run_simulation()` |
| `app.py` | Sliders, compare button, tables, charts, CSV download | `streamlit`, `run_simulation()` call |
| `tests/test_simulation.py` | Repeatability, completed patient count, doctor limits, baseline activation tests | `test_*` functions |
| `requirements.txt` | Packages and version constraints | `simpy`, `pandas`, `matplotlib`, `streamlit`, `pytest` |
| `pytest.ini` | Adds the root to the Python path for pytest | `pythonpath = .` |
| `.gitignore` | Keeps virtual environments, caches and generated outputs out of version control | Ignore patterns |
| `README.md` | Provides the startup commands and model overview | Project documentation |
| `docs/HOSPITAL_SIMULATION_PROJECT_GUIDE.md` | Walks through setup, runs and code | This guide |
| `docs/CODEX_TASK.md` | Implementation milestones, assumptions, research comparison protocol | Text document, no executable code |
| `src/__init__.py` | Python package marker | Currently empty |

### Read the code in execution order

1. **`main.py`** uses an `if __name__ == "__main__"` guard. Running the file parses arguments and calls `run_experiment()`; importing it leaves the CLI idle.
2. **`src/experiment.py`** loops over seeds starting at 0. For each seed, it calls the simulator for each policy, adds policy and seed columns to patient records, builds a table of runs, and averages the metrics by policy. Pandas writes the CSVs and Matplotlib saves the bar chart.
3. **`src/simulation.py`** owns simulated time and state. `generate_patients()` samples demand before the run. `run_simulation()` creates a SimPy environment and one `GradeStation` per grade, starts one `serve()` process per patient, and starts `control_loop()` to poll staffing once a minute. `done()` lets the run finish after all patients complete treatment. The function returns `(records, timeline, summary)`.
4. **`app.py`** calls the simulator directly for each policy using the selected seed. It saves the report and combined patient records in `st.session_state`, so the results remain visible across reruns with the same inputs. The group-by on policy and grade produces the second chart. The combined patient table supplies the CSV download.
5. **`tests/test_simulation.py`** calls the simulator directly to check deterministic patient generation, patient conservation, grade staffing bounds, and zero baseline backup activations.

## 2. Prerequisites and opening project

- Install **Python 3.10 or newer** (the project uses supported modern Python; verify individual package compatibility for your Python version).
- Use any terminal and editor. For VS Code interpreter selection, install the Microsoft Python extension.
- If you received an archive, extract it. Open the folder containing `main.py` in VS Code: **File > Open Folder**.
- Open a VS Code terminal: **Terminal > New Terminal**.
- All commands below assume your terminal is at the **project root**, next to `main.py`.

Check location and files:

**macOS / Linux terminal**
```bash
pwd
ls
ls src
python3 --version
```

**Windows PowerShell**
```powershell
Get-Location
Get-ChildItem
Get-ChildItem src
py --version
```

**Windows Command Prompt (cmd)**
```bat
cd
dir
dir src
py --version
```

If you see `ModuleNotFoundError: No module named 'src'`, make sure `src/simulation.py`, `src/experiment.py` and `src/__init__.py` exist *inside* the project and you are in the project root.

## 3. First-time setup — macOS (including Mac M1)

Run these **one line at a time** in VS Code's terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m pytest -q
```

When activated, the prompt usually shows `(.venv)`. In VS Code, use **Command Palette > Python: Select Interpreter** and select `.venv/bin/python`.

If `python` cannot be found after activation, use `.venv/bin/python` explicitly.

## 4. First-time setup — Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m pytest -q
```

If PowerShell blocks `Activate.ps1`, you can avoid changing security settings by calling the venv Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Or, if your computer permits it, use the temporary process-only policy and then activate:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Choose `.venv\Scripts\python.exe` via **Python: Select Interpreter** in VS Code.

## 5. First-time setup — Windows Command Prompt (cmd.exe)

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m pip check
python -m pytest -q
```

## 6. Run the 3 policies together in terminal

All three run automatically using the command below (there is currently **no policy flag** in `main.py`). You do **not** need Codex just to run comparisons.

```bash
python main.py --repetitions 20 --patients 100 --arrival 5
```

Parameter definitions:

| Argument | Meaning | Example |
| --- | --- | --- |
| `--repetitions` | Number of random seeds / repeated runs per policy | `20` |
| `--patients` | Total synthetic patients per run | `100` |
| `--arrival` | **Mean minutes between arrivals**, not patients per minute | `5` |

Example: 20 repetitions × 3 policies = 60 individual simulation runs. Each policy uses the same seed for a given repetition, allowing paired comparisons of demand and sampled service durations.

To run **baseline alone**, **original ORB alone**, or **improved alone**, the current CLI does not provide a `--policy` option. Instead, run them individually using the short Python commands below (works on macOS, PowerShell and cmd, provided the environment is active):

**Baseline only:**
```bash
python -c "from src.simulation import run_simulation; print(run_simulation('baseline', n=100, mean_interarrival=5, seed=42)[2])"
```

**Original ORB only:**
```bash
python -c "from src.simulation import run_simulation; print(run_simulation('orb', n=100, mean_interarrival=5, seed=42)[2])"
```

**Improved ORB only:**
```bash
python -c "from src.simulation import run_simulation; print(run_simulation('improved', n=100, mean_interarrival=5, seed=42)[2])"
```

These commands print a single-seed summary to the terminal. The CLI comparison in section 6 writes the aggregated files.

### Solo run with a patient trace

Run `improved` under heavier demand and inspect patient 1 and the initial staffing snapshot:

```bash
python -c "from src.simulation import run_simulation; records, timeline, summary = run_simulation('improved', n=100, mean_interarrival=1, seed=42); print(records.head(1).round(3).to_string(index=False)); print(timeline.head(4).to_string(index=False))"
```

Patient 1 is grade I, arrives at minute 1.020, and spends 3.813 minutes in registration and triage. It waits 0 minutes for a doctor and departs at minute 18.169. The next four rows show the four grade stations at minute 0. The simulator records one timeline row per grade per poll, with the observed queue length and the active staffing after that poll's decision.

### Compare all three on the same seed as the solo run

```bash
python -c "import pandas as pd; from src.simulation import run_simulation; policies = ('baseline', 'orb', 'improved'); print(pd.DataFrame([run_simulation(p, n=100, mean_interarrival=1, seed=42)[2] for p in policies])[['policy', 'mean_queue_wait', 'p95_queue_wait', 'activations']].round(3).to_string(index=False))"
```

```text
  policy  mean_queue_wait  p95_queue_wait  activations
baseline           29.083          82.234            0
     orb           11.269          35.640            2
improved           15.938          41.292            4
```

Waits are in minutes. On this seed, fixed-threshold ORB had the shortest mean and p95 waits. To reproduce these same settings in the dashboard, choose 100 patients, a 1.0-minute interval, and seed 42. The CLI uses seeds starting at 0, so `--repetitions 1` uses seed 0.

## 7. Compare arrival rates (high to low congestion)

**macOS / Linux** (run from project root):
```bash
for rate in 1 2 5 10 20; do
  echo "========== MEAN ARRIVAL INTERVAL: $rate MIN =========="
  python main.py --repetitions 20 --patients 100 --arrival "$rate"
done
```

**Windows PowerShell:**
```powershell
foreach ($rate in 1, 2, 5, 10, 20) {
  Write-Host "========== MEAN ARRIVAL INTERVAL: $rate MIN =========="
  python main.py --repetitions 20 --patients 100 --arrival $rate
}
```

**Windows Command Prompt (interactive cmd):**
```bat
for %r in (1 2 5 10 20) do (
  echo ====== ARRIVAL %r MIN ======
  python main.py --repetitions 20 --patients 100 --arrival %r
)
```

**Note:** In a saved `.bat` script, use `%%r` rather than `%r`. On *interactive* cmd, `%r` is correct.

**Important:** Every run of `main.py` saves to the same `outputs/` filenames. In a loop, **only the last arrival-rate scenario remains in CSV and PNG files**, even though all scenario tables are printed to terminal. To preserve each scenario, copy the output files after every run or call the experiment function with a separate directory, for example `python -c "from src.experiment import run_experiment; print(run_experiment(20, 100, 1, output_dir='outputs/arrival_1').to_string(index=False))"`. Do not treat the last saved `summary.csv` as covering all five arrival rates.

## 8. Run the visual dashboard

**macOS / Windows PowerShell / Windows cmd:**
```bash
python -m streamlit run app.py
```

Streamlit typically prints a local address such as `http://localhost:8501` and opens it in your browser. In the interface:
1. Select **Number of patients**.
2. Select **Mean arrival interval (minutes)**.
3. Select **Random seed**.
4. Click **Compare policies**.
5. Read the comparison table and plots; optionally click **Download patient data (CSV)**.

**Dashboard vs CLI:** `app.py` runs **one seed per policy** each time you click Compare. `main.py` uses multiple seeds/repetitions and writes aggregate CSV/PNG output. Do not compare their tables as if they have the same sampling method.

## 9. How to stop, reopen, exit, and restart

| Action | macOS / Linux | Windows PowerShell / cmd |
| --- | --- | --- |
| Stop Streamlit or running experiment | Press **Control + C** in the active terminal | Press **Ctrl + C** (cmd may ask `Terminate batch job?`; answer `Y` if so) |
| Close web interface | Close its browser tab (server must separately be stopped) | Same |
| Restart dashboard | `python -m streamlit run app.py` | Same |
| Rerun comparison | `python main.py --repetitions 20 --patients 100 --arrival 5` | Same |
| Exit virtual environment | `deactivate` | `deactivate` |
| Reactivate later | `source .venv/bin/activate` | PowerShell: `.\.venv\Scripts\Activate.ps1`; cmd: `.venv\Scripts\activate.bat` |
| Leave terminal | `exit` | `exit` |

Do **not** type `deactivate` to stop Streamlit first: interrupt its running process with **Ctrl+C**.

## 10. Interpret all output columns correctly

| Column | Meaning / caution |
| --- | --- |
| `policy` | `baseline` (fixed doctors), `orb` (queue-threshold backup), `improved` (proposed pressure-based backup) |
| `mean_queue_wait` | Average wait **after registration and triage**, before receiving a treatment doctor (minutes) |
| `p95_queue_wait` | 95th percentile of doctor-queue waits (minutes); in `main.py` this is the **average of each run's p95**, not pooled p95 |
| `mean_sojourn` | Average total time from ED arrival to completed treatment, including modeled registration, triage, queue, treatment (minutes) |
| `deadline_violations` | Average per-run count of waits above grade-specific simulation targets; thresholds are **assumptions**, not medical safety recommendations |
| `activations` | Mean number of backup-staff activation events per run; e.g., 0.25 means 5 activation events in total across 20 runs |
| `max_queue` | Mean over runs of the maximum **combined** queue size observed across grades at each sampled minute |

**Less is usually better** for waiting and queue metrics, but more activations can mean more temporary staffing use. A fair improvement claim should also evaluate backup-doctor minutes and per-grade outcomes.

## 11. Locate outputs

After running `main.py`, open `outputs/`:
- `summary.csv`: one row per policy, containing average metrics across repetitions.
- `all_runs.csv`: policy-by-seed summary records for each run.
- `patients.csv`: patient-level observations for every policy and seed (synthetic data).
- `waiting_comparison.png`: mean doctor-queue-wait comparison plot.

For a quick inspection:

**macOS:**
```bash
open outputs/waiting_comparison.png
open outputs/summary.csv
```

**Windows PowerShell:**
```powershell
Invoke-Item .\outputs\waiting_comparison.png
Invoke-Item .\outputs\summary.csv
```

**Windows Command Prompt:**
```bat
start "" outputs\waiting_comparison.png
start "" outputs\summary.csv
```

## 12. What the three algorithms actually do

### From arrival to departure

`generate_patients()` uses a seeded random number generator. The first patient arrives after an exponential gap, and each subsequent arrival adds another exponential gap using the chosen mean. Grades I–IV have probabilities of 10%, 15%, 30%, and 45%. Registration takes a uniform 2–4 minutes, triage is exponential with a mean of 5 minutes, and treatment is exponential with a mean of 10 minutes. The code samples grade and all durations before starting SimPy, so a policy's staffing decisions cannot change the arrival or service draws for that seed.

After registration and triage, `serve()` records the time the patient entered their grade's treatment queue. It requests a doctor token from the grade's `simpy.Store`. If all doctors are busy, the request waits. Once granted, the process holds the token for the treatment duration, returns it to the store, then records departure. Each token represents one exclusive doctor. The four stations start with 4, 3, 2, and 2 base doctors and can add up to 3, 2, 1, and 1 backups, respectively.

In a patient record, `arrival + pre_treatment_time` gives the treatment start minute. `service_time` sums the three stage durations, while `sojourn_time = departure - arrival` includes time waiting for a doctor. The patient CSV combines these records with policy and seed so you can compare the same patient across policies.

### Baseline (`policy="baseline"`)
Uses four separate grade stations with fixed doctor counts. No backup staff is activated.

### Paper-like ORB (`policy="orb"`)
Every simulated minute, checks the grade-specific waiting queue. If `queue_length > queue_threshold` (default threshold 5), it adds a backup doctor when the grade's backup limit allows. Each poll activates at most one backup per grade. If the queue is empty at a poll, it releases at most one idle backup per grade. A busy backup retains its token until treatment finishes. **Simplification:** no explicit delay for transferring backup staff; this is not a complete Petri-net reproduction.

### Proposed improved ORB (`policy="improved"`)
Every simulated minute, estimates a pressure score from waiting queue length, expected treatment workload, available active doctor count, oldest waiting time, and configured grade-specific targets. The formula is `(queue_length * 10 / active_doctors + oldest_wait) / grade_target`. Active doctors include base staff and activated backups, whether idle or busy. The grade targets are 2, 10, 30, and 90 simulated minutes for grades I–IV. With a nonempty queue, it activates at most one backup per grade per poll when `pressure >= improved_trigger` (default 0.8), subject to backup limits. Releases idle backups when no one is waiting. This is research-prototype logic and requires testing, not a proven upgrade.

**Original paper vs code:** The paper's workflow includes multiple stages and timed Petri-net transitions. Current code simplifies registration and triage to uncontended delays, does not model detailed exams or ward outcomes, and only represents treatment doctors as resource tokens. `docs/CODEX_TASK.md` lists fidelity improvements.

## 13. Debugging common issues

**`ModuleNotFoundError: No module named 'src'`**
- Check that `pytest.ini` is beside `main.py` and `src/` contains `simulation.py`, `experiment.py`, and `__init__.py`.
- Run from the **root folder** where `main.py` exists, not from inside `src/`.
- Check with `ls src` (Mac) / `dir src` (Windows).

**`No module named simpy`, `streamlit`, `pytest`**
- Activate `.venv` and run: `python -m pip install -r requirements.txt`.
- Verify: `python -m pip --version`.

**`python` points to wrong environment**
- Mac: `which python` should usually end in `.venv/bin/python`.
- Windows: `where python` (cmd) or `Get-Command python` (PowerShell) should point at `.venv`.
- VS Code: select `.venv` as interpreter.

**Port `8501` already in use**
- Stop the previous Streamlit server with Ctrl+C. Alternatively run:
  `python -m streamlit run app.py --server.port 8502`.

**Tests pass but output differs from paper**
- Passing tests confirms only the **tested properties** of this starter; it does not validate full STPN modeling or match the original paper's reported numbers. Fix fidelity gaps before asserting reproduction.

**Tests or simulation freeze**
- Stop with Ctrl+C, record the exact traceback/last printed command, check package installation, and inspect `src/simulation.py`'s `done()` and doctor-resource release logic.

## 14. Suggested end-to-end research workflow

1. **Setup:** install dependencies; run `python -m pytest -q`.
2. **Sanity run:** `python main.py --repetitions 20 --patients 100 --arrival 5`.
3. **Visual check:** `python -m streamlit run app.py`; compare all policies for one seed.
4. **Congestion sweep:** run arrival intervals 1, 2, 5, 10, 20 minutes; save each scenario's outputs separately.
5. **Code walkthrough:** open `generate_patients()`, `GradeStation`, `serve()`, `control_loop()` and understand token flow.
6. **Reproduction milestone:** implement explicit STPN elements, transition delays and missing workflow resources; write tests.
7. **Extension milestone:** evaluate proposed pressure-based ORB with paired random seeds, grade-specific waiting, tail wait, staffing usage, sensitivity analysis.
8. **Report:** include paper assumptions, what was genuinely replicated, differences, results, graphs, limitations and exact commands.


---

**Safety and attribution:** This uses simulated, synthetic patients and is for academic demonstration only. It should not be used for real hospital staffing or clinical treatment decisions. A full reproduction of published results requires a separately validated model with the paper's exact net topology, inputs, workflow semantics, and experimental settings.
