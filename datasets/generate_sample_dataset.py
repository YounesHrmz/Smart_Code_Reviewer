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

RULE_DETAILS = {
    "with_open": {
        "target_statement": "with open()",
        "problem_description": "فتح الملف دون سياق with يمكن أن يسبب تسرب موارد.",
        "explanation": "استخدام open() بدون with لا يضمن إغلاق الملف تلقائياً عند انتهاء التنفيذ أو حدوث استثناء.",
        "recommendation": "استبدل open() بـ with open(...) لإغلاق الملف تلقائياً وإدارة الموارد بشكل آمن.",
    },
    "eval": {
        "target_statement": "eval()",
        "problem_description": "تنفيذ eval() يعرض التطبيق لحقن كود غير موثوق.",
        "explanation": "eval() يقوم بتفسير سلسلة نصية ككود بايثون، مما يسمح بتنفيذ أوامر خطيرة من المدخلات.",
        "recommendation": "استخدم حلول آمنة لتحليل البيانات بدلاً من eval().",
    },
    "exec": {
        "target_statement": "exec()",
        "problem_description": "استخدام exec() يسمح بتنفيذ كود غير آمن.",
        "explanation": "exec() ينفذ نص بايثون ديناميكي، مما يجعل من الصعب ضمان سلامة المحتوى.",
        "recommendation": "استبدل exec() بمنطق ثابت أو واجهات تحليل آمنة.",
    },
    "os_system": {
        "target_statement": "os.system()",
        "problem_description": "استدعاء os.system() يمكن أن يؤدي لحقن أوامر.",
        "explanation": "تمرير سلاسل نصية إلى shell قد يؤدي إلى تنفيذ أوامر غير متوقعة.",
        "recommendation": "استخدم subprocess.run() مع shell=False وتمرير قائمة معاملات.",
    },
    "subprocess_shell": {
        "target_statement": "subprocess.Popen(..., shell=True)",
        "problem_description": "استخدام shell=True يفتح ثغرة حقن أوامر.",
        "explanation": "تمرير أمر كسلسلة إلى shell يعرض التطبيق لمخاطر من بيانات المستخدم.",
        "recommendation": "استعمل قائمة معاملات صريحة و shell=False بدلاً من shell=True.",
    },
    "pickle_loads": {
        "target_statement": "pickle.loads()",
        "problem_description": "pickle.loads() يعالج بيانات قابلة للتنفيذ قد تحتوي على كود خبيث.",
        "explanation": "تحميل بيانات pickle من مصدر غير موثوق يمكن أن يؤدي إلى تنفيذ كائنات ضارة.",
        "recommendation": "استعمل JSON أو بروتوكولات آمنة أخرى بدلاً من pickle.",
    },
    "yaml_load": {
        "target_statement": "yaml.load()",
        "problem_description": "yaml.load() يقرأ YAML غير آمن.",
        "explanation": "yaml.load() يمكن أن ينشئ كائنات تنفيذية من المحتوى.",
        "recommendation": "استخدم yaml.safe_load() وتحقق من مصداقية المصدر.",
    },
    "nested_if": {
        "target_statement": "nested if",
        "problem_description": "تداخل شرطى عميق يزيد صعوبة القراءة.",
        "explanation": "الكود المتداخل جداً يجعل تتبع التدفق وفهم المنطق أكثر تعقيداً.",
        "recommendation": "قسم الشرطيات إلى دوال مساعدة أو استخدم guard clauses.",
    },
    "bad_variable_name": {
        "target_statement": "poor variable naming",
        "problem_description": "أسماء المتغيرات غير الوصفية تقلل من وضوح الكود.",
        "explanation": "الأسماء الغامضة مثل tmp أو x لا تعكس الغرض من المتغير.",
        "recommendation": "استخدم أسماء وصفية تعكس المحتوى أو الوظيفة.",
    },
    "semicolon": {
        "target_statement": "semicolon statement",
        "problem_description": "استخدام الفاصلة المنقوطة في سطر واحد يقلل من الوضوح.",
        "explanation": "دمج عدة تعليمات في سطر واحد يجعل الكود أقل قابلية للقراءة.",
        "recommendation": "افصل التعليمات على أسطر مستقلة.",
    },
    "generic": {
        "target_statement": "generic issue",
        "problem_description": "تم اكتشاف مشكلة محتملة في هذا المقطع البرمجي.",
        "explanation": "راجع هذا المقطع برمجياً لتحديد السبب الدقيق وتحسينه.",
        "recommendation": "حسّن البنية والتسمية لتقليل المخاطر والأخطاء.",
    },
}


def infer_rule_details(snippet: str, label: str) -> dict:
    code = snippet.lower()
    if "eval(" in code:
        return RULE_DETAILS["eval"]
    if "exec(" in code:
        return RULE_DETAILS["exec"]
    if "os.system" in code:
        return RULE_DETAILS["os_system"]
    if "subprocess.Popen" in code and "shell=True" in code:
        return RULE_DETAILS["subprocess_shell"]
    if "pickle.loads" in code:
        return RULE_DETAILS["pickle_loads"]
    if "yaml.load" in code:
        return RULE_DETAILS["yaml_load"]
    if "with open" in code:
        return RULE_DETAILS["with_open"]
    if " if " in code and code.count("if ") > 1:
        return RULE_DETAILS["nested_if"]
    if any(token in code for token in ["tmp", " x ", " y ", " z "]):
        return RULE_DETAILS["bad_variable_name"]
    if ";" in code:
        return RULE_DETAILS["semicolon"]
    return RULE_DETAILS["generic"]


rows = []
for example in examples:
    rule = infer_rule_details(example["snippet"], example["label"])
    rows.append(
        {
            "code_snippet": example["snippet"].strip(),
            "predicted_category": example["category"],
            "predicted_label": example["label"],
            "confidence_score": f"{example['confidence']:.2f}",
            "target_statement": rule["target_statement"],
            "problem_description": rule["problem_description"],
            "explanation": rule["explanation"],
            "recommendation": rule["recommendation"],
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
    rule = infer_rule_details(snippet, template["label"])
    rows.append(
        {
            "code_snippet": snippet,
            "predicted_category": template["category"],
            "predicted_label": template["label"],
            "confidence_score": f"{confidence:.2f}",
            "target_statement": rule["target_statement"],
            "problem_description": rule["problem_description"],
            "explanation": rule["explanation"],
            "recommendation": rule["recommendation"],
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
            "target_statement",
            "problem_description",
            "explanation",
            "recommendation",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"generated {len(rows)} rows -> {path}")
