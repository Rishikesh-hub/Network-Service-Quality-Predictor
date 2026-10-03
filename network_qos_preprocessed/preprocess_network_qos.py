"""
Network Service Quality Predictor - preprocessing pipeline
Files expected in the same folder as this script:
1. dataset_01_TC33_27062025_labeled dataset4.csv
2. dataset_02_TC33_02072025_labeled dataset 3.csv
3. wue_tput_all_Throughput dataset 2.csv
4. ntnu_tput_all_Throughput dataset1.csv

Outputs:
- qos_labeled_cleaned.csv
- train/validation/test CSV splits
- model-ready ANN/Logistic matrices
- preprocessing summary JSON

Important:
- The two labeled files are combined because they have the same schema.
- Duplicate timestamp+link records are removed.
- Rows without LABEL are excluded from supervised training.
- LABEL 0/1/2 is retained as severity.
- degradation = 1 for LABEL 1 or 2, else 0.
- Scaling/imputation is fitted ONLY on the training set to avoid data leakage.
- Throughput files are cleaned separately; they are not blindly merged because they have
  no LABEL and no common timestamp+link key.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.ensemble import RandomForestClassifier

BASE = Path(".")
OUT = BASE / "network_qos_preprocessed"
OUT.mkdir(exist_ok=True)

LABELED_FILES = [
    BASE / "dataset_01_TC33_27062025_labeled dataset4.csv",
    BASE / "dataset_02_TC33_02072025_labeled dataset 3.csv",
]

# -----------------------------
# 1. Load + combine labeled data
# -----------------------------
frames = [pd.read_csv(p) for p in LABELED_FILES]
raw = pd.concat(frames, ignore_index=True)

rows_before = len(raw)

# A repeated timestamp+link is the same measurement key in these files.
# No conflicting LABEL values were found for the duplicated keys.
raw = raw.drop_duplicates(subset=["timestamp", "link"], keep="first").copy()
rows_after_dedup = len(raw)

# -----------------------------
# 2. Remove rows without target
# -----------------------------
df = raw[raw["LABEL"].notna()].copy()
df["LABEL"] = df["LABEL"].astype(int)

# Binary alert target: 0 = normal, 1 = degraded
df["degradation"] = (df["LABEL"] > 0).astype(int)

# -----------------------------
# 3. Timestamp feature engineering
# -----------------------------
df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
df["hour"] = df["datetime"].dt.hour
df["day_of_week"] = df["datetime"].dt.dayofweek
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

# Cyclic encoding prevents 23:00 and 00:00 from looking far apart
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

df = df.sort_values(["timestamp", "link"]).reset_index(drop=True)
df.to_csv(OUT / "qos_labeled_cleaned.csv", index=False)

# -----------------------------
# 4. Chronological split
# -----------------------------
# Time split is preferred for this forecasting-style problem.
n = len(df)
i1 = int(n * 0.70)
i2 = int(n * 0.85)

train = df.iloc[:i1].copy()
val   = df.iloc[i1:i2].copy()
test  = df.iloc[i2:].copy()

train.to_csv(OUT / "train_cleaned.csv", index=False)
val.to_csv(OUT / "validation_cleaned.csv", index=False)
test.to_csv(OUT / "test_cleaned.csv", index=False)

# -----------------------------
# 5. Select model features
# -----------------------------
# Do not use raw timestamp or datetime directly.
# 'avalability' is constant in the supplied labeled data, so it is removed.
drop_cols = [
    "LABEL", "degradation", "timestamp", "datetime",
    "avalability"
]

feature_cols = [c for c in df.columns if c not in drop_cols]

X_train = train[feature_cols]
X_val = val[feature_cols]
X_test = test[feature_cols]

y_train_binary = train["degradation"]
y_val_binary = val["degradation"]
y_test_binary = test["degradation"]

# -----------------------------
# 6. Preprocessing
# -----------------------------
numeric_cols = X_train.select_dtypes(include=["number"]).columns.tolist()
categorical_cols = X_train.select_dtypes(exclude=["number"]).columns.tolist()

numeric_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", RobustScaler())
])

categorical_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipe, numeric_cols),
    ("cat", categorical_pipe, categorical_cols)
])

# Fit ONLY on train
Xtr = preprocessor.fit_transform(X_train)
Xva = preprocessor.transform(X_val)
Xte = preprocessor.transform(X_test)

feature_names = preprocessor.get_feature_names_out()

pd.DataFrame(Xtr, columns=feature_names).to_csv(OUT / "X_train_ann_logistic.csv", index=False)
pd.DataFrame(Xva, columns=feature_names).to_csv(OUT / "X_validation_ann_logistic.csv", index=False)
pd.DataFrame(Xte, columns=feature_names).to_csv(OUT / "X_test_ann_logistic.csv", index=False)

pd.DataFrame({"target": y_train_binary}).to_csv(OUT / "y_train_binary.csv", index=False)
pd.DataFrame({"target": y_val_binary}).to_csv(OUT / "y_validation_binary.csv", index=False)
pd.DataFrame({"target": y_test_binary}).to_csv(OUT / "y_test_binary.csv", index=False)

# -----------------------------
# 7. Clean supplementary throughput datasets
# -----------------------------
for filename in [
    "wue_tput_all_Throughput dataset 2.csv",
    "ntnu_tput_all_Throughput dataset1.csv",
]:
    p = BASE / filename
    if p.exists():
        t = pd.read_csv(p)
        if "Unnamed: 0" in t.columns:
            t = t.drop(columns=["Unnamed: 0"])
        t.columns = [c.strip().lower() for c in t.columns]
        for c in t.select_dtypes(include="object").columns:
            t[c] = t[c].astype(str).str.strip()
        out_name = (
            "wue_throughput_cleaned.csv"
            if filename.startswith("wue_")
            else "ntnu_throughput_cleaned.csv"
        )
        t.to_csv(OUT / out_name, index=False)

summary = {
    "raw_combined_rows": rows_before,
    "rows_after_timestamp_link_dedup": rows_after_dedup,
    "unlabeled_rows_removed": int(rows_after_dedup - len(df)),
    "final_labeled_rows": len(df),
    "severity_counts": df["LABEL"].value_counts().sort_index().to_dict(),
    "binary_degradation_counts": df["degradation"].value_counts().sort_index().to_dict(),
    "train_rows": len(train),
    "validation_rows": len(val),
    "test_rows": len(test),
    "model_features_after_encoding": len(feature_names),
    "numeric_features": numeric_cols,
    "categorical_features": categorical_cols,
}

with open(OUT / "preprocessing_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=int)

print(json.dumps(summary, indent=2))
