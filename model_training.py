"""Train a RandomForest model on processed data.
Saves model to models/best_model.pkl and test split to data/processed/X_test.csv/y_test.csv
"""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
MODELS = BASE / "models"
MODELS.mkdir(parents=True, exist_ok=True)


def main():
    print("Loading processed data...")
    X_path = PROCESSED / "X_processed.csv"
    y_path = PROCESSED / "y_processed.csv"
    if not X_path.exists() or not y_path.exists():
        raise FileNotFoundError("Processed data not found. Run data_preprocessing first.")

    X = pd.read_csv(X_path)
    y = pd.read_csv(y_path).squeeze()

    print(f"Data shape: X={X.shape}, y={y.shape}")

    print("Splitting data into train/test (80/20)")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training RandomForestClassifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    print("Evaluating on test set...")
    preds = clf.predict(X_test)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)

    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")
    print("\nFull classification report:")
    print(classification_report(y_test, preds, zero_division=0))

    # save model and test split
    model_path = MODELS / "best_model.pkl"
    joblib.dump(clf, model_path)
    # Also save a deployment-friendly name
    model_path2 = MODELS / "model.pkl"
    joblib.dump(clf, model_path2)
    X_test.to_csv(PROCESSED / "X_test.csv", index=False)
    pd.DataFrame({'target': y_test}).to_csv(PROCESSED / "y_test.csv", index=False)
    print(f"Model saved to {model_path} and {model_path2}")


if __name__ == '__main__':
    main()
