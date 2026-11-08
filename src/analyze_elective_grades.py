import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "subject_grade_distribution.csv"

df = pd.read_csv(DATA_PATH)

grade_table = pd.crosstab(
    df["preferred_subject_category"],
    df["academic_outcome"]
)

print("\n===== SUBJECT CATEGORY vs ACADEMIC OUTCOME =====")
print(grade_table)

grade_table.to_csv(OUTPUT_PATH)

print("\nSaved analysis to:", OUTPUT_PATH)
