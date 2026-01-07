"""Evaluate saved model on test data and optionally save confusion matrix plot."""
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
MODELS = BASE / "models"
REPORTS = BASE / "reports"


def main():
    model_path = MODELS / "best_model.pkl"
    X_test_path = PROCESSED / "X_test.csv"
    y_test_path = PROCESSED / "y_test.csv"

    if not model_path.exists():
        raise FileNotFoundError("Model not found. Run model_training first.")

    print("Loading model and test data...")
    clf = joblib.load(model_path)
    X_test = pd.read_csv(X_test_path)
    y_test = pd.read_csv(y_test_path).squeeze()

    preds = clf.predict(X_test)
    print("Classification report:")
    print(classification_report(y_test, preds, zero_division=0))

    cm = confusion_matrix(y_test, preds)
    print("Confusion matrix:\n", cm)

    # Save plot if reports dir exists
    if REPORTS.exists():
        REPORTS.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(5, 4))
        im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
        ax.set_title('Confusion Matrix')
        for (i, j), val in np.ndenumerate(cm):
            ax.text(j, i, int(val), ha='center', va='center', color='red')
        out = REPORTS / 'confusion_matrix.png'
        plt.tight_layout()
        plt.savefig(out)
        print(f"Saved confusion matrix to {out}")


if __name__ == '__main__':
    main()
