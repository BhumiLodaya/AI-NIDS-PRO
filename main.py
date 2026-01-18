import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
SRC_DIR = BASE_DIR / "src"
MODELS_DIR = BASE_DIR / "models"

DEFAULT_DATASET_SRC = Path(r"C:\Users\bhumi\OneDrive\Desktop\professional\AI_Threat_Analysis_NIDS\02-14-2018.csv")


def ensure_dirs():
    for d in [DATA_RAW, DATA_PROCESSED, SRC_DIR, MODELS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def copy_dataset():
    if not DEFAULT_DATASET_SRC.exists():
        print(f"Warning: source dataset not found at {DEFAULT_DATASET_SRC}")
        return
    dest = DATA_RAW / DEFAULT_DATASET_SRC.name
    if dest.exists():
        print(f"Dataset already present at {dest}")
        return
    shutil.copy(DEFAULT_DATASET_SRC, dest)
    print(f"Copied dataset to {dest}")


def run_script(path):
    print(f"Running {path}...")
    subprocess.check_call(["python", str(path)])


def main():
    ensure_dirs()
    copy_dataset()

    # Run preprocessing then training
    preprocessing = SRC_DIR / "data_preprocessing.py"
    training = SRC_DIR / "model_training.py"

    if preprocessing.exists():
        run_script(preprocessing)
    else:
        print(f"{preprocessing} not found; please create it before running")

    if training.exists():
        run_script(training)
    else:
        print(f"{training} not found; please create it before running")


if __name__ == "__main__":
    main()
