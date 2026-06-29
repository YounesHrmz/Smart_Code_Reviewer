import csv
from pathlib import Path

path = Path("datasets/sample_training_data.csv")
with path.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
print(len(rows))
