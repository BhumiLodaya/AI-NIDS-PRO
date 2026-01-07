"""Load trained model and predict on new data.
Usage:
 python src/predict.py --file path/to/new.csv
 or
 python src/predict.py --vector 1,2,3,4,...
"""
import argparse
from pathlib import Path

import joblib
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent.parent
MODELS = BASE / "models"
PROCESSED = BASE / "data" / "processed"



def load_model():
    model_path = MODELS / "best_model.pkl"
    if not model_path.exists():
        model_path = MODELS / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError("Model not found. Run model_training first.")
    return joblib.load(model_path)

def load_scaler():
    scaler_path = MODELS / "scaler.pkl"
    if scaler_path.exists():
        return joblib.load(scaler_path)
    return None

def load_encoders():
    enc_path = MODELS / "encoder.pkl"
    if enc_path.exists():
        return joblib.load(enc_path)
    return None


def load_feature_columns():
    cols_path = PROCESSED / "feature_columns.txt"
    if not cols_path.exists():
        return None
    with open(cols_path, 'r', encoding='utf-8') as f:
        cols = [l.strip() for l in f if l.strip()]
    return cols


def predict_from_file(model, file_path):
    print(f"Loading and predicting from file: {file_path}")
    cols = load_feature_columns()
    encoders = load_encoders() or {}
    scaler = load_scaler()

    # Determine expected columns
    if cols is None:
        raise FileNotFoundError("Feature columns metadata not found at data/processed/feature_columns.txt")
    expected_cols = cols
    print(f"Expecting {len(expected_cols)} features")

    chunksize = 10000
    reader = pd.read_csv(file_path, chunksize=chunksize)
    out_path = None
    first = True
    total = 0
    for chunk in reader:
        total += len(chunk)
        # Validate columns
        if list(chunk.columns) != expected_cols:
            # If columns are same set but different order, reorder; else raise
            if set(chunk.columns) == set(expected_cols):
                chunk = chunk[expected_cols]
            else:
                raise ValueError(f"Input CSV columns do not match expected features.\nExpected:\n{expected_cols}\nFound:\n{list(chunk.columns)}")

        # Apply encoders
        for col, categories in encoders.items():
            if col in chunk.columns:
                chunk[col] = pd.Categorical(chunk[col], categories=categories).codes

        # Scale numeric columns (those not in encoders)
        numeric_cols = [c for c in expected_cols if c not in encoders]
        if scaler and numeric_cols:
            # ensure numeric order
            chunk[numeric_cols] = scaler.transform(chunk[numeric_cols])

        # Predict
        preds = model.predict(chunk)
        probs = model.predict_proba(chunk)

        results = pd.DataFrame({
            'prediction': ['Normal' if int(p) == 0 else 'Attack' for p in preds],
            'confidence': [float(np.max(pr)) for pr in probs]
        })

        if out_path:
            results.to_csv(out_path, mode='a', header=False, index=False)
        elif out_path is None and 'save_path' in locals():
            pass
        else:
            # if no save requested, print first 10 predictions for this chunk
            for i, row in results.head(10).iterrows():
                print(f"Row {i}: {row['prediction']} (confidence: {row['confidence']:.3f})")

        # If saving requested, caller can set save_path in locals (we'll handle in wrapper)

    print(f"Processed {total} rows")

def predict_from_vector(model, vector_str):
    vals = [float(x) for x in vector_str.split(',')]
    arr = np.array(vals).reshape(1, -1)
    cols = load_feature_columns()
    if cols is not None and arr.shape[1] != len(cols):
        raise ValueError(f"Input vector has length {arr.shape[1]} but model expects {len(cols)} features")
    scaler = load_scaler()
    if scaler:
        arr = scaler.transform(arr)
    p = model.predict(arr)[0]
    prob = np.max(model.predict_proba(arr))
    label = "Normal" if int(p) == 0 else "Attack"
    print(f"Prediction: {label} (confidence: {prob:.3f})")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='CSV file with rows to predict')
    parser.add_argument('--vector', type=str, help='Single sample as comma separated values')
    parser.add_argument('--save', type=str, help='Optional path to save predictions CSV')
    args = parser.parse_args()

    model = load_model()
    if args.file:
        if args.save:
            # define save_path variable in predict_from_file scope via locals hack
            globals()['save_path'] = args.save
        predict_from_file(model, args.file)
    elif args.vector:
        predict_from_vector(model, args.vector)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
