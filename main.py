import argparse
from src.experiment import run_experiment

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--patients", type=int, default=100)
    parser.add_argument("--arrival", type=float, default=5.0,
                        help="Mean minutes between patient arrivals")
    args = parser.parse_args()
    result = run_experiment(args.repetitions, args.patients, args.arrival)
    print(result.to_string(index=False))
    print("\nSaved CSVs and chart to outputs/")
