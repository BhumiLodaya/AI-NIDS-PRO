# Dataset Setup Guide

## Download the CIC-IDS-2018 Dataset

This project requires the **CIC-IDS-2018** dataset, which is not included in this repository due to its large size (341 MB).

### Steps to Download:

1. **Visit the Official Source:**
   - URL: https://www.unb.ca/cic/datasets/ids-2018.html
   - Provider: Canadian Institute for Cybersecurity (CIC)

2. **Download the Dataset:**
   - Download the **Wednesday, February 14, 2018** file
   - Filename: `02-14-2018.csv`

3. **Place in Project Directory:**
   ```
   AI_Threat_Analysis_NIDS/
   └── data/
       └── raw/
           └── 02-14-2018.csv  ← Place here
   ```

   Or place it in the root directory - the `main.py` script will copy it to `data/raw/`

### Dataset Details:

- **Size**: ~341 MB (compressed) / ~358 MB (uncompressed)
- **Records**: 822,947+ network flow samples
- **Features**: 80+ network traffic attributes
- **Labels**: Normal traffic and various attack types (DoS, DDoS, Brute Force, etc.)

### Alternative: Use Sample Data

For testing purposes, the preprocessing script supports sampling:

```powershell
# Process only 10,000 rows for quick testing
python src\data_preprocessing.py --sample-size 10000
```

### After Download:

1. Verify the file is named exactly `02-14-2018.csv`
2. Run the preprocessing pipeline:
   ```powershell
   python main.py
   ```
   or
   ```powershell
   python run_pipeline.py
   ```

## Processed Data

The following files will be generated after preprocessing:
- `data/processed/X_processed.csv` (~1.1 GB)
- `data/processed/X_test.csv` (~216 MB)
- `data/processed/y_processed.csv` (~2.3 MB)
- `data/processed/y_test.csv` (~0.5 MB)

These are also excluded from the repository and will be regenerated on your machine.
