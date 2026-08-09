from pathlib import Path
import csv
import random
import textwrap

path = Path(__file__).with_name("sample_training_data.csv")
random.seed(42)

examples = [
    {
        "category": "clean_code",
        "label": "good",
        "snippet": textwrap.dedent("""
            def normalize_username(username: str) -> str:
                "Return a clean lowercase username."
                if username is None:
                    return ""
                return username.strip().lower()
            """),
        "confidence": 0.97,
    },
    {
        "category": "clean_code",
        "label": "good",
        "snippet": textwrap.dedent("""
            class FileReader:
                def __init__(self, path: str):
                    self.path = path

                def read(self) -> str:
                    with open(self.path, "r", encoding="utf-8") as f:
                        return f.read()
            """),
        "confidence": 0.96,
    },
    {
        "category": "clean_code",
        "label": "good",
        "snippet": textwrap.dedent("""
            def parse_list(items):
                return [item.strip() for item in items if isinstance(item, str)]
            """),
        "confidence": 0.95,
    },
    {
        "category": "clean_code",
        "label": "bad",
        "snippet": textwrap.dedent("""
            def calc(x, y):
                res = x + y
                return res

            def do_it(a, b):
                total = a + b
                return total
            """),
        "confidence": 0.88,
    },
    {
        "category": "clean_code",
        "label": "bad",
        "snippet": textwrap.dedent("""
            def load_data(path):
                f = open(path, 'r')
                return f.read()
            """),
        "confidence": 0.89,
    },
    {
        "category": "clean_code",
        "label": "bad",
        "snippet": textwrap.dedent("""
            def calculate(x):
                tmp = x * 2
                return tmp
            """),
        "confidence": 0.87,
    },
    {
        "category": "quality",
        "label": "good",
        "snippet": textwrap.dedent("""
            def safe_sum(numbers):
                if not numbers:
                    return 0
                return sum(numbers)
            """),
        "confidence": 0.95,
    },
    {
        "category": "quality",
        "label": "good",
        "snippet": textwrap.dedent("""
            def is_even(value):
                return value % 2 == 0
            """),
        "confidence": 0.94,
    },
    {
        "category": "quality",
        "label": "good",
        "snippet": textwrap.dedent("""
            def find_positive(values):
                return [v for v in values if v > 0]
            """),
        "confidence": 0.93,
    },
    {
        "category": "quality",
        "label": "bad",
        "snippet": textwrap.dedent("""
            def average(values):
                return sum(values) / len(values)
            """),
        "confidence": 0.87,
    },
    {
        "category": "quality",
        "label": "bad",
        "snippet": textwrap.dedent("""
            def check_status(flag):
                if flag == True:
                    return 'enabled'
                else:
                    return 'disabled'
            """),
        "confidence": 0.88,
    },
    {
        "category": "quality",
        "label": "bad",
        "snippet": textwrap.dedent("""
            def filter_items(items):
                result = []
                for item in items:
                    if item is not None:
                        result.append(item)
                return result
            """),
        "confidence": 0.89,
    },
    {
        "category": "security",
        "label": "good",
        "snippet": textwrap.dedent("""
            import subprocess

            def list_files(path):
                return subprocess.run(["ls", path], capture_output=True, text=True, check=True).stdout
            """),
        "confidence": 0.95,
    },
    {
        "category": "security",
        "label": "good",
        "snippet": textwrap.dedent("""
            import hashlib

            def hash_password(password: str) -> str:
                return hashlib.sha256(password.encode('utf-8')).hexdigest()
            """),
        "confidence": 0.94,
    },
    {
        "category": "security",
        "label": "good",
        "snippet": textwrap.dedent("""
            import yaml

            def load_config(data):
                return yaml.safe_load(data)
            """),
        "confidence": 0.93,
    },
    {
        "category": "security",
        "label": "bad",
        "snippet": textwrap.dedent("""
            import os

            def delete_all_files(path):
                os.system('rm -rf /')
            """),
        "confidence": 0.98,
    },
    {
        "category": "security",
        "label": "bad",
        "snippet": textwrap.dedent("""
            import pickle

            def load_data(blob):
                return pickle.loads(blob)
            """),
        "confidence": 0.96,
    },
    {
        "category": "security",
        "label": "bad",
        "snippet": textwrap.dedent("""
            import requests

            def get_remote(url):
                return requests.get(url, verify=False).text
            """),
        "confidence": 0.95,
    },
    {
        "category": "security",
        "label": "bad",
        "snippet": textwrap.dedent("""
            import subprocess

            def run_shell(command):
                subprocess.Popen(command, shell=True)
            """),
        "confidence": 0.96,
    },
]

templates = [
    {
        "category": "clean_code",
        "label": "good",
        "template": textwrap.dedent("""
            def {name}(items):
                if items is None:
                    return []
                return [item.strip() for item in items if isinstance(item, str)]
            """),
        "confidence_range": (0.91, 0.97),
    },
    {
        "category": "clean_code",
        "label": "good",
        "template": textwrap.dedent("""
            def {name}(path):
                with open(path, 'r', encoding='utf-8') as file:
                    return file.read()
            """),
        "confidence_range": (0.90, 0.96),
    },
    {
        "category": "clean_code",
        "label": "bad",
        "template": textwrap.dedent("""
            def {name}(a, b):
                tmp = a + b
                return tmp
            """),
        "confidence_range": (0.84, 0.90),
    },
    {
        "category": "clean_code",
        "label": "bad",
        "template": textwrap.dedent("""
            def {name}(items):
                result = []
                for item in items:
                    if item is not None:
                        result.append(item)
                return result
            """),
        "confidence_range": (0.85, 0.91),
    },
    {
        "category": "quality",
        "label": "good",
        "template": textwrap.dedent("""
            def {name}(items):
                if items is None:
                    return []
                return [item for item in items if item is not None]
            """),
        "confidence_range": (0.90, 0.96),
    },
    {
        "category": "quality",
        "label": "good",
        "template": textwrap.dedent("""
            def {name}(values):
                total = 0
                for value in values:
                    if value >= 0:
                        total += value
                return total
            """),
        "confidence_range": (0.88, 0.94),
    },
    {
        "category": "quality",
        "label": "bad",
        "template": textwrap.dedent("""
            def {name}(flag):
                if flag == True:
                    return 'yes'
                return 'no'
            """),
        "confidence_range": (0.84, 0.90),
    },
    {
        "category": "quality",
        "label": "bad",
        "template": textwrap.dedent("""
            def {name}(items):
                result = []
                for item in items:
                    if item != None:
                        result.append(item)
                return result
            """),
        "confidence_range": (0.85, 0.91),
    },
    {
        "category": "security",
        "label": "good",
        "template": textwrap.dedent("""
            import requests

            def {name}(url):
                response = requests.get(url, timeout=10, verify=True)
                response.raise_for_status()
                return response.text
            """),
        "confidence_range": (0.90, 0.96),
    },
    {
        "category": "security",
        "label": "good",
        "template": textwrap.dedent("""
            import yaml

            def {name}(data):
                return yaml.safe_load(data)
            """),
        "confidence_range": (0.89, 0.95),
    },
    {
        "category": "security",
        "label": "bad",
        "template": textwrap.dedent("""
            import pickle

            def {name}(blob):
                return pickle.loads(blob)
            """),
        "confidence_range": (0.92, 0.98),
    },
    {
        "category": "security",
        "label": "bad",
        "template": textwrap.dedent("""
            import requests

            def {name}(url):
                return requests.get(url, verify=False).text
            """),
        "confidence_range": (0.91, 0.97),
    },
]

rows = []
for example in examples:
    rows.append(
        {
            "code_snippet": example["snippet"].strip(),
            "predicted_category": example["category"],
            "predicted_label": example["label"],
            "confidence_score": f"{example['confidence']:.2f}",
        }
    )

unique_names = [
    "format_names",
    "calculate_total",
    "safe_divide",
    "clean_list",
    "update_config",
    "filter_items",
    "process_data",
    "build_summary",
    "validate_input",
    "read_file",
    "check_status",
    "split_lines",
    "format_text",
    "parse_items",
    "load_config",
    "validate_data",
    "fetch_remote",
    "hash_password",
    "execute_command",
    "sanitize_input",
    "compute_sum",
    "validate_items",
]

for index in range(1000 - len(rows)):
    template = random.choice(templates)
    name = f"{random.choice(unique_names)}_{index}"
    snippet = template["template"].format(name=name).strip()
    if template["category"] == "security" and template["label"] == "good":
        snippet = snippet.replace(
            "requests.get(url, timeout=10)",
            "requests.get(url, timeout=10, verify=True)",
        )

    confidence = round(random.uniform(*template["confidence_range"]), 2)
    rows.append(
        {
            "code_snippet": snippet,
            "predicted_category": template["category"],
            "predicted_label": template["label"],
            "confidence_score": f"{confidence:.2f}",
        }
    )

# Ensure the dataset is ordered and balanced in a repeatable way.
rows.sort(
    key=lambda r: (
        r["predicted_category"],
        r["predicted_label"],
        float(r["confidence_score"]),
    )
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
