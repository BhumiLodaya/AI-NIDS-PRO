"""Run the full pipeline end-to-end: preprocessing -> training -> evaluation -> optional prediction.

Usage examples:
  python run_pipeline.py --sample-size 10000
  python run_pipeline.py --predict-file new_samples.csv
  python run_pipeline.py --predict-vector 0.1,0.2,0.3
"""
import argparse
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "src"


def run_preprocessing(sample_size=None):
    cmd = ["python", str(SRC / "data_preprocessing.py")]
    if sample_size:
        cmd += ["--sample-size", str(sample_size)]
    print("Running preprocessing:", " ".join(cmd))
    subprocess.check_call(cmd)


def run_training():
    cmd = ["python", str(SRC / "model_training.py")]
    print("Running training:", " ".join(cmd))
    subprocess.check_call(cmd)


def run_evaluation():
    cmd = ["python", str(SRC / "evaluate_model.py")]
    print("Running evaluation:", " ".join(cmd))
    subprocess.check_call(cmd)


def run_prediction(file=None, vector=None):
    cmd = ["python", str(SRC / "predict.py")]
    if file:
        cmd += ["--file", file]
    if vector:
        cmd += ["--vector", vector]
    print("Running prediction:", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-size', type=int, help='Process only N rows (quick test)')
    parser.add_argument('--predict-file', type=str, help='CSV to predict after pipeline')
    parser.add_argument('--predict-vector', type=str, help='Single sample vector to predict')
    args = parser.parse_args()

    run_preprocessing(sample_size=args.sample_size)
    run_training()
    run_evaluation()

    if args.predict_file or args.predict_vector:
        run_prediction(file=args.predict_file, vector=args.predict_vector)


if __name__ == '__main__':
    main()
