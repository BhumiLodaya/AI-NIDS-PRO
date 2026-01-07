"""Memory-safe data preprocessing with optional sampling and controlled encoding.

Usage:
  python src/data_preprocessing.py [--sample]

Outputs:
  data/processed/X_processed.csv
  data/processed/y_processed.csv
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)


DROP_HIGH_CARDINALITY = [
	"Flow ID",
	"Source IP",
	"Destination IP",
	"Source Port",
	"Destination Port",
	"Timestamp",
]


def load_dataset(filename=None):
	if filename:
		path = Path(filename)
	else:
		files = list(RAW.glob("*.csv"))
		if not files:
			raise FileNotFoundError(f"No CSV found in {RAW}")
		path = files[0]
	print(f"Loading {path}")
	df = pd.read_csv(path)
	return df


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
	print("Cleaning data: replacing inf/-inf with NaN, dropping fully-null cols and duplicates")
	df = df.replace([np.inf, -np.inf], np.nan)
	df = df.dropna(axis=1, how='all')
	df = df.drop_duplicates()
	df = df.dropna(axis=1, how='all')
	return df


import joblib

def efficient_encode(X: pd.DataFrame, models_dir: Path) -> pd.DataFrame:
	print("Encoding categorical columns efficiently...")

	# Drop known high-cardinality or non-feature columns safely
	X = X.drop(columns=DROP_HIGH_CARDINALITY, errors='ignore')

	# Identify categorical columns
	cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
	print(f"Categorical columns found: {len(cat_cols)}")

	encoders = {}
	small_cardinality = []
	for c in cat_cols:
		n_unique = X[c].nunique(dropna=False)
		if n_unique < 50:
			small_cardinality.append(c)
		else:
			print(f"Dropping high-cardinality column '{c}' ({n_unique} unique values)")
			X = X.drop(columns=[c], errors='ignore')

	# For small cardinality columns, use category codes (memory-efficient)
	for c in small_cardinality:
		print(f"Label-encoding column '{c}' with {X[c].nunique(dropna=False)} unique values")
		X[c] = X[c].astype('category')
		encoders[c] = X[c].cat.categories.tolist()
		X[c] = X[c].cat.codes

	# Save encoders as a dict: {col: categories_list}
	if encoders:
		enc_path = models_dir / "encoder.pkl"
		joblib.dump(encoders, enc_path)
		print(f"Saved label encoders to {enc_path}")

	return X


def preprocess(df: pd.DataFrame, models_dir: Path):
	# Find target column
	target_cols = [c for c in df.columns if c.lower() == 'label' or c.lower() == 'attack']
	if not target_cols:
		raise KeyError("Could not find target column named 'Label' or similar")
	target_col = target_cols[0]

	print(f"Using target column: {target_col}")
	y = df[target_col].astype(str)
	X = df.drop(columns=[target_col], errors='ignore')

	# Efficient categorical handling
	X = efficient_encode(X, models_dir)

	# Numeric columns remain unchanged
	numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
	print(f"Numeric columns to scale: {len(numeric_cols)}")

	# Fill NaNs before scaling
	X = X.fillna(0)

	# Scale numeric features
	scaler = StandardScaler()
	if numeric_cols:
		print("Scaling numeric features...")
		X[numeric_cols] = scaler.fit_transform(X[numeric_cols].astype(float))
		# Save scaler
		scaler_path = models_dir / "scaler.pkl"
		joblib.dump(scaler, scaler_path)
		print(f"Saved scaler to {scaler_path}")

	# Encode target to binary: BENIGN/Normal -> 0, others -> 1
	y_encoded = y.apply(lambda v: 0 if v.strip().lower() in ('benign', 'normal', '0') else 1)

	# Decide whether to apply SMOTE: only if small-ish dataset
	X_res, y_res = X, y_encoded
	try:
		from imblearn.over_sampling import SMOTE
		rows = X.shape[0]
		if rows <= 200000:
			print(f"Applying SMOTE to balance classes (rows={rows})")
			sm = SMOTE(random_state=42)
			X_res, y_res = sm.fit_resample(X, y_encoded)
		else:
			print(f"Skipping SMOTE due to large dataset size ({rows} rows).")
	except Exception as e:
		print("SMOTE not applied (missing or failed):", e)

	return X_res, y_res


def save_processed(X, y):
	X_path = PROCESSED / "X_processed.csv"
	y_path = PROCESSED / "y_processed.csv"
	print(f"Saving processed X to {X_path} and y to {y_path}")
	X.to_csv(X_path, index=False)
	# y may be a Series; save as single-column CSV
	pd.DataFrame({'target': y}).to_csv(y_path, index=False)
	# Save feature columns metadata for prediction validation
	try:
		cols_path = PROCESSED / "feature_columns.txt"
		with open(cols_path, 'w', encoding='utf-8') as f:
			for c in X.columns:
				f.write(f"{c}\n")
		print(f"Saved feature columns to {cols_path}")
	except Exception as e:
		print("Warning: failed to save feature columns metadata:", e)


def main():
	MODELS = BASE / "models"
	MODELS.mkdir(parents=True, exist_ok=True)
	import argparse

	parser = argparse.ArgumentParser(description='Preprocess CIC-IDS CSV')
	parser.add_argument('filename', nargs='?', help='Optional path to CSV file to process')
	parser.add_argument('--sample', action='store_true', help='Legacy: use sample of 10000 rows')
	parser.add_argument('--sample-size', type=int, help='Process only N rows (quick test)')
	args = parser.parse_args()

	df = load_dataset(args.filename)

	# determine sampling
	if args.sample_size is not None:
		n = args.sample_size
		if df.shape[0] > n:
			print(f"⚡ Using sample of {n} rows for testing")
			df = df.sample(n=n, random_state=42)
		else:
			print(f"Dataset smaller than sample size ({df.shape[0]} rows); using full dataset")
	elif args.sample:
		n = 10000
		if df.shape[0] > n:
			print(f"⚡ Using sample of {n} rows for testing")
			df = df.sample(n=n, random_state=42)
		else:
			print(f"Dataset smaller than sample size ({df.shape[0]} rows); using full dataset")

	df = clean_df(df)
	X, y = preprocess(df, MODELS)
	save_processed(X, y)


if __name__ == '__main__':
	main()

