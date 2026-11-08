import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"

df = pd.read_csv(DATA_PATH)

print("\n===== DATASET VALIDATION =====")
print("Total responses:", len(df))
print("Total columns:", len(df.columns))
print("Unique respondent IDs:", df["respondent_id"].nunique())

print("\n===== REQUIRED CHECKS =====")
print("Exactly 25 responses:", len(df) == 25)
print("Unique respondent IDs:", df["respondent_id"].is_unique)
print("Missing respondent IDs:", df["respondent_id"].isna().sum())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== PREFERRED SUBJECT CATEGORIES =====")
print(df["preferred_subject_category"].value_counts())

print("\n===== ACADEMIC OUTCOMES =====")
print(df["academic_outcome"].value_counts())

print("\n===== VALIDATION COMPLETE =====")
