import argparse
from src.experiment import run_experiment

# Parse terminal arguments only when this file is run directly.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Each repetition uses one shared random seed for all three policies.
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--patients", type=int, default=100)
    parser.add_argument("--arrival", type=float, default=5.0,
                        help="Mean minutes between patient arrivals")
    args = parser.parse_args()

    # The experiment writes the output files and returns the averaged table.
    result = run_experiment(args.repetitions, args.patients, args.arrival)
    print(result.to_string(index=False))
    print("\nSaved CSVs and chart to outputs/")
