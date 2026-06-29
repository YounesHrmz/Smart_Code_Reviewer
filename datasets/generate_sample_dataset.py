from pathlib import Path
import csv

path = Path(__file__).with_name("sample_training_data.csv")

patterns = {
    "clean_code": [
        "def normalize_name(name):\n    return name.strip().lower()",
        "def build_summary(items):\n    summary = []\n    for item in items:\n        summary.append(str(item))\n    return summary",
        "class ConfigLoader:\n    def __init__(self):\n        self.value = 1\n\n    def read(self):\n        return self.value",
        "def load_settings(path):\n    with open(path, 'r') as handle:\n        return handle.read()",
        "def safe_divide(a, b):\n    if b == 0:\n        return None\n    return a / b",
    ],
    "quality": [
        "def check_status(flag):\n    if flag:\n        return 'enabled'\n    return 'disabled'",
        "def get_average(nums):\n    if not nums:\n        return 0\n    return sum(nums) / len(nums)",
        "def parse_value(value):\n    if value is None:\n        return 0\n    return int(value)",
        "def loop_example(items):\n    count = 0\n    for item in items:\n        count += 1\n    return count",
        "def contains_even(nums):\n    return any(num % 2 == 0 for num in nums)",
    ],
    "security": [
        "import os\nos.remove('file.txt')",
        "import subprocess\nsubprocess.call(['whoami'])",
        "import yaml\nobj = yaml.load(content)",
        "import requests\nrequests.get(url, verify=False)",
        "import pickle\npickle.loads(payload)",
    ],
}

rows = []
# Start from a few high-quality seed samples
seed_rows = [
    ("def add(a, b):\n    return a + b", "clean_code", "good", 0.96),
    (
        "def calculate_total(items):\n    total = 0\n    for item in items:\n        total += item\n    return total",
        "clean_code",
        "good",
        0.94,
    ),
    ("import os\nos.system('rm -rf /')", "security", "bad", 0.97),
    ("import subprocess\nsubprocess.call(['echo', 'hello'])", "security", "bad", 0.95),
    (
        "def bad_name(x, y, z):\n    tmp = x + y + z\n    return tmp",
        "clean_code",
        "bad",
        0.92,
    ),
    (
        "def analyze(value):\n    if value > 0:\n        return 'positive'\n    return 'non-positive'",
        "quality",
        "good",
        0.91,
    ),
]
for code, category, label, conf in seed_rows:
    rows.append(
        {
            "code_snippet": code,
            "predicted_category": category,
            "predicted_label": label,
            "confidence_score": str(conf),
        }
    )

for index in range(1000 - len(rows)):
    cat = ["clean_code", "quality", "security"][index % 3]
    label = "good" if cat != "security" else "bad"
    if cat == "quality" and index % 5 == 0:
        label = "bad"
    if cat == "clean_code" and index % 7 == 0:
        label = "bad"
    code = patterns[cat][index % len(patterns[cat])]
    code = code + f"\n# sample row {index + len(rows) + 1}"
    confidence = round(0.85 + (index % 15) * 0.01, 2)
    rows.append(
        {
            "code_snippet": code,
            "predicted_category": cat,
            "predicted_label": label,
            "confidence_score": str(confidence),
        }
    )

with path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "code_snippet",
            "predicted_category",
            "predicted_label",
            "confidence_score",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"generated {len(rows)} rows -> {path}")
