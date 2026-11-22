HOSPITAL ED SIMULATION COMMANDS
Run from the project folder containing main.py. Lines beginning with # explain the next command.

1. CREATE AND ACTIVATE THE ENVIRONMENT (first time)
# Create the virtual environment on macOS or Linux.
```bash
python3 -m venv .venv
```
# Activate it on macOS or Linux (repeat in each new terminal).
```bash
source .venv/bin/activate

# On Windows, create the environment with the Python launcher.
```bash
py -m venv .venv
```

# Activate it in Windows PowerShell (repeat in each new terminal).
```bash
.\.venv\Scripts\Activate.ps1
```

# In Windows Command Prompt, use this activation command instead.
```bash
.venv\Scripts\activate.bat
```

2. INSTALL AND VERIFY (all platforms after activation)
# Install the project's dependencies into the active environment.
```bash
python -m pip install -r requirements.txt
```

# Check that the installed packages have compatible dependencies.
```bash
python -m pip check
```

# Run the simulation's automated tests.

```bash
python -m pytest -q
```

# List the CLI options and their usage.

```bash
python main.py --help
```
3. RUN ONE POLICY (100 patients, 1-minute mean arrival interval, seed 42)
# Run baseline alone and print its summary.
```bash
python -c "from src.simulation import run_simulation; print(run_simulation('baseline', n=100, mean_interarrival=1, seed=42)[2])"


# Run fixed-threshold ORB alone and print its summary.
```bash
python -c "from src.simulation import run_simulation; print(run_simulation('orb', n=100, mean_interarrival=1, seed=42)[2])"
```bash

# Run improved ORB alone and print its summary.
```bash
python -c "from src.simulation import run_simulation; print(run_simulation('improved', n=100, mean_interarrival=1, seed=42)[2])"
```
4. RUN COMPARISONS AND EXPERIMENTS
# Compare all three policies under the same settings and seed as the solo runs.
```bash
python -c "import pandas as pd; from src.simulation import run_simulation; print(pd.DataFrame([run_simulation(p, n=100, mean_interarrival=1, seed=42)[2] for p in ('baseline', 'orb', 'improved')]).to_string(index=False))"
```
# Run all three policies across 20 shared seeds with 100 patients per run and a 5-minute mean arrival interval, replacing the standard CSVs and PNG in outputs/.
```bash
python main.py --repetitions 20 --patients 100 --arrival 5
```
# Sweep five mean arrival intervals in minutes and save each 20-seed comparison in its own outputs/arrival_* folder.
```bash
python -c "from src.experiment import run_experiment; [print(f'Arrival interval {a} min', run_experiment(20, 100, a, output_dir=f'outputs/arrival_{a}').to_string(index=False), sep=chr(10)) for a in (1, 2, 5, 10, 20)]"
```
# Print the standard comparison summary after running main.py.
```bash
python -c "from pathlib import Path; print(Path('outputs/summary.csv').read_text())"
```
# Open the standard comparison chart on macOS after running main.py.
```bash
open outputs/waiting_comparison.png
```
5. START AND STOP THE STREAMLIT DASHBOARD
# Start the dashboard, open the printed local URL, then choose inputs and click Compare policies.
```bash
python -m streamlit run app.py
```
# Use port 8502 if the default port is occupied.
```bash
python -m streamlit run app.py --server.port 8502
```

# Press Ctrl+C in the server terminal to stop Streamlit.
# After the server stops, leave the virtual environment.
deactivate

# Data flow

User runs main.py
    ↓
argparse reads terminal options
    ↓
args.repetitions, args.patients, args.arrival
    ↓
main.py calls run_experiment(...)
    ↓
experiment loops over random seeds
    ↓
experiment calls run_simulation(...) for each policy
    ↓
simulation generates patient objects
    ↓
SimPy processes arrival, registration, triage, queue, and treatment
    ↓
run_simulation() creates:
    patient DataFrame
    timeline DataFrame
    summary dictionary
    ↓
experiment combines repeated runs
    ↓
pandas creates averaged table
    ↓
CSV files and PNG chart are written
    ↓
main.py prints the averaged table