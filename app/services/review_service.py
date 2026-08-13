import ast
import json
import os
import re
from typing import Any, Dict, List, Tuple

from app.analyzers.ast_parser import ASTParser
from app.analyzers.clean_code_rule import CleanCodeAnalyzer
from app.analyzers.complexity_rule import ComplexityAnalyzer
from app.analyzers.security_rules import SecurityAnalyzer
from app.config import Config
from app.ml.self_learning import AutonomousLearningLoop
from app.repositories.audit_repository import AuditRepository

RULE_TEMPLATE_PATH = os.path.join(Config.DATASET_DIR, "rule_templates.json")


DEFAULT_RULE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "with_open": {
        "target_statement": '<code dir="ltr">with open()</code>',
        "problem_description": "المشكلة: عبارة {target_statement} في السطر {line_number} داخل {function_name} قد تسبب تسرب موارد.",
        "explanation": 'استخدام <code dir="ltr">open()</code> بدون with لا يضمن إغلاق الملف تلقائياً عند انتهاء التنفيذ أو حدوث خطأ.',
        "actionable_recommendation": 'استبدل <code dir="ltr">open()</code> بـ <code dir="ltr">with open(...)</code> لإدارة الموارد الآمنة.',
    },
    "eval": {
        "target_statement": '<code dir="ltr">eval()</code>',
        "problem_description": "المشكلة: عبارة {target_statement} في السطر {line_number} داخل {function_name} تعرض التطبيق لحقن كود.",
        "explanation": '<code dir="ltr">eval()</code> يقوم بتفسير سلسلة نصية ككود بايثون، مما يسمح بتنفيذ أوامر ضارة من محتوى المستخدم.',
        "actionable_recommendation": 'استبدل <code dir="ltr">eval()</code> بمكتبات تحليل آمنة أو دوال للتحويل المباشر بدلاً من تنفيذ النصوص.',
    },
    "exec": {
        "target_statement": '<code dir="ltr">exec()</code>',
        "problem_description": "المشكلة: عبارة {target_statement} في السطر {line_number} داخل {function_name} قد تنفذ كوداً غير آمن.",
        "explanation": '<code dir="ltr">exec()</code> ينفذ نص بايثون ديناميكي، مما يجعل من الصعب ضمان سلامة المحتوى.',
        "actionable_recommendation": 'استبدل <code dir="ltr">exec()</code> بمنطق ثابت أو واجهات تحليل آمنة.',
    },
    "os_system": {
        "target_statement": '<code dir="ltr">os.system()</code>',
        "problem_description": "المشكلة: عبارة {target_statement} في السطر {line_number} داخل {function_name} قد تؤدي إلى حقن أوامر.",
        "explanation": "تمرير سلاسل نصية إلى shell يعرض النظام لمخاطر تنفيذ أوامر غير متوقعة.",
        "actionable_recommendation": 'استخدم <code dir="ltr">subprocess.run([...], shell=False)</code> بدلاً من <code dir="ltr">os.system()</code>.',
    },
    "subprocess_shell": {
        "target_statement": '<code dir="ltr">subprocess.Popen(..., shell=True)</code>',
        "problem_description": "المشكلة: عبارة {target_statement} في السطر {line_number} داخل {function_name} تعرض التطبيق لحقن أوامر.",
        "explanation": "تمرير أمر كسلسلة إلى shell يسمح بحقن مدخلات غير آمنة.",
        "actionable_recommendation": 'استخدم قائمة معاملات صريحة و <code dir="ltr">shell=False</code> بدلاً من <code dir="ltr">shell=True</code>.',
    },
    "pickle_loads": {
        "target_statement": '<code dir="ltr">pickle.loads()</code>',
        "problem_description": "المشكلة: عبارة {target_statement} في السطر {line_number} داخل {function_name} قد تعالج بيانات خبيثة.",
        "explanation": "تحميل بيانات pickle من مصدر غير موثوق يمكن أن يؤدي إلى تنفيذ كائنات ضارة.",
        "actionable_recommendation": 'استخدم <code dir="ltr">json.loads()</code> أو بروتوكولات آمنة بدلاً من pickle.',
    },
    "yaml_load": {
        "target_statement": '<code dir="ltr">yaml.load()</code>',
        "problem_description": "المشكلة: عبارة {target_statement} في السطر {line_number} داخل {function_name} قد تفسر محتوى غير آمن.",
        "explanation": '<code dir="ltr">yaml.load()</code> يمكن أن ينشئ كائنات تنفيذية من المحتوى.',
        "actionable_recommendation": 'استعمل <code dir="ltr">yaml.safe_load()</code> وتحقق من مصدر البيانات.',
    },
    "nested_if": {
        "target_statement": "nested if",
        "problem_description": "التداخل الشرطي العميق يزيد صعوبة القراءة والصيانة.",
        "explanation": "الكود المتداخل جداً يجعل تتبع التدفق وفهم المنطق أكثر تعقيداً.",
        "actionable_recommendation": "قلل التداخل بفصل الشرطيات إلى دوال مساعدة أو استخدم guard clauses.",
    },
    "bad_variable_name": {
        "target_statement": "poor variable naming",
        "problem_description": "استخدام أسماء متغيرات غير معبرة يقلل من وضوح الكود.",
        "explanation": 'الأسماء الغامضة مثل <code dir="ltr">tmp</code> أو <code dir="ltr">x</code> لا تعبر عن الغرض.',
        "actionable_recommendation": "استخدم أسماء وصفية تعبر عن المحتوى أو الوظيفة.",
    },
    "semicolon": {
        "target_statement": "semicolon statement",
        "problem_description": "استخدام الفاصلة المنقوطة في سطر واحد يقلل من الوضوح.",
        "explanation": "دمج عدة تعليمات في سطر واحد يجعل الكود أقل قابلية للقراءة.",
        "actionable_recommendation": "افصل التعليمات على أسطر مستقلة واحتفظ بتعبير واحد لكل سطر.",
    },
    "sql_injection": {
        "target_statement": "sql string concatenation",
        "problem_description": "بناء استعلام SQL عن طريق ربط سلاسل نصية يعرض النظام لحقن بيانات.",
        "explanation": "الاستعلامات غير المهيكلة باستخدام concatenation تسمح بحقن إدخالات ضارة.",
        "actionable_recommendation": "استخدم استعلامات parameterized أو ORM بدلاً من ربط النصوص.",
    },
    "hardcoded_secret": {
        "target_statement": "hardcoded secret assignment",
        "problem_description": "المشكلة: تخزين سر أو مفتاح في الشيفرة في السطر {line_number} داخل {function_name} يعرض السر للانكشاف.",
        "explanation": "تضمين أسرار مثل كلمات المرور أو مفاتيح API في الشيفرة يؤدي إلى تسربها عبر نظام التحكم بالإصدار أو بيئات النشر.",
        "actionable_recommendation": "انقل الأسرار إلى متغيرات بيئة أو مدير أسرار (Vault) وطبق تدوير ومراقبة وصول.",
    },
    "command_injection": {
        "target_statement": "command string concatenation",
        "problem_description": "تمرية أوامر نظامية كسلسلة قد تؤدي إلى حقن أوامر.",
        "explanation": "تمرير مدخلات المستخدم مباشرة إلى دوال النظام يفتح باب تنفيذ أوامر غير آمنة.",
        "actionable_recommendation": 'استخدم قائمة معاملات ولا تفعّل <code dir="ltr">shell</code> إذا أمكن.',
    },
    "generic": {
        "target_statement": "problematic statement",
        "problem_description": "تم اكتشاف مشكلة في هذا المقطع البرمجي.",
        "explanation": "هذا المقطع يحتاج مراجعة لتحديد السبب الدقيق وتحسين الجودة.",
        "actionable_recommendation": "راجع الكود وحسّن الهيكلية والتسمية لتقليل المخاطر.",
    },
}


def _load_rule_templates() -> Dict[str, Dict[str, str]]:
    """Load rule templates from JSON file or fall back to defaults."""
    if os.path.exists(RULE_TEMPLATE_PATH):
        try:
            with open(RULE_TEMPLATE_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return DEFAULT_RULE_TEMPLATES
    return DEFAULT_RULE_TEMPLATES


RULE_TEMPLATES = _load_rule_templates()


def save_default_rule_templates(path: str = RULE_TEMPLATE_PATH) -> None:
    """Persist default templates and merge missing keys into existing file.

    Non-fatal: failures are ignored to avoid breaking app startup.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(DEFAULT_RULE_TEMPLATES, fh, ensure_ascii=False, indent=2)
            return

        with open(path, "r", encoding="utf-8") as fh:
            existing = json.load(fh)

        merged = dict(existing)
        changed = False
        for key, val in DEFAULT_RULE_TEMPLATES.items():
            if key not in merged:
                merged[key] = val
                changed = True

        if changed:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(merged, fh, ensure_ascii=False, indent=2)
    except Exception:
        return


def reload_rule_templates() -> None:
    """Reload templates into module-level `RULE_TEMPLATES`."""
    global RULE_TEMPLATES
    RULE_TEMPLATES = _load_rule_templates()


class CodeReviewService:
    """Static code review service combining AST rules and a learning loop.

    Responsibilities:
    - Run analyzers per snippet
    - Map analyzer findings to rule templates
    - Persist audit logs
    """

    def __init__(self) -> None:
        self.learning_loop = AutonomousLearningLoop()
        self.audit_repo = AuditRepository()

    @staticmethod
    def _format_reference(code: str) -> str:
        tokens = [tok for tok in re.split(r"\W+", code) if tok]
        for tok in reversed(tokens):
            if tok.isidentifier() and len(tok) > 1:
                return tok
        return code.strip().splitlines()[0][:40]

    def _find_rule_key(self, code: str, issues: List[str]) -> str:
        """Determine the best matching rule key using AST-aware checks.

        Falls back to regex heuristics when AST parsing fails.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            tree = None

        # quick regex for hardcoded secrets (fast path)
        if re.search(
            r"(?i)(password|passwd|secret|token|api_key|aws_key|access_key)\s*=\s*['\"][^'\"]+['\"]",
            code,
        ):
            return "hardcoded_secret"

        if tree is not None:
            # detect dangerous calls and patterns precisely
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    # os.system()
                    if isinstance(func, ast.Attribute) and isinstance(
                        func.value, ast.Name
                    ):
                        if func.value.id == "os" and func.attr == "system":
                            return "os_system"
                        if func.value.id == "subprocess" and func.attr in (
                            "Popen",
                            "call",
                            "run",
                            "check_output",
                        ):
                            for kw in getattr(node, "keywords", []):
                                if (
                                    kw.arg == "shell"
                                    and getattr(kw.value, "value", None) is True
                                ):
                                    return "subprocess_shell"

                    # direct name calls: eval, exec, open, pickle/yaml names
                    if isinstance(func, ast.Name):
                        if func.id in ("eval", "exec"):
                            return func.id
                        if func.id == "open" and "with" not in code.splitlines()[0]:
                            return "with_open"

                    # attribute calls like pickle.loads or yaml.load
                    if isinstance(func, ast.Attribute) and isinstance(
                        func.value, ast.Name
                    ):
                        if func.value.id == "pickle" and func.attr == "loads":
                            return "pickle_loads"
                        if func.value.id == "yaml" and func.attr == "load":
                            return "yaml_load"

            # SQL concatenation detection
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("execute", "executemany", "executescript")
                ):
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                            return "sql_injection"

        # fallback heuristics
        normalized = code.lower()
        if re.search(r"\beval\s*\(", normalized):
            return "eval"
        if re.search(r"\bexec\s*\(", normalized):
            return "exec"
        if re.search(r"\bos\.system\s*\(", normalized):
            return "os_system"
        if "subprocess.popen" in normalized and "shell=true" in normalized:
            return "subprocess_shell"
        if re.search(r"\bpickle\.loads\s*\(", normalized):
            return "pickle_loads"
        if re.search(r"\byaml\.load\s*\(", normalized):
            return "yaml_load"
        if re.search(r"\bopen\s*\(", normalized) and not re.search(
            r"\bwith\s+open\s*\(", normalized
        ):
            return "with_open"
        if re.search(r"\b(tmp|x|y|z|temp|data|val|var|foo|bar)\b", normalized):
            return "bad_variable_name"
        if ";" in code:
            return "semicolon"
        return "generic"

    def _build_rule_details(
        self,
        issues: list[str],
        line: int,
        scope_name: str,
        code: str,
    ) -> tuple[str, str, str, str]:
        scope_label = scope_name if scope_name != "global" else "المستوى العام"
        rule_key = self._find_rule_key(code, issues)
        rule = RULE_TEMPLATES.get(rule_key, RULE_TEMPLATES["generic"])
        target_statement = rule["target_statement"]
        problem_description = rule["problem_description"].format(
            target_statement=target_statement,
            line_number=line,
            function_name=scope_label,
        )
        explanation_text = rule["explanation"]
        recommendation_text = rule["actionable_recommendation"]
        return (
            target_statement,
            problem_description,
            explanation_text,
            recommendation_text,
        )

    def process_file_analysis(self, filename: str, source_code: str) -> dict:
        parser = ASTParser(source_code)
        if not parser.is_valid():
            return {
                "error": "خطأ في بناء الجملة: الملف المرسل ليس بايثون صالحًا.",
                "summary": {"total_issues": 0, "recommendations": []},
                "report": [],
            }

        snippets = parser.get_snippets()
        if not snippets:
            snippets = [
                {
                    "line_no": idx + 1,
                    "code": line.strip(),
                    "scope_label": "على المستوى العام",
                    "node_type": "سطر",
                    "identifiers": [],
                }
                for idx, line in enumerate(source_code.splitlines())
                if line.strip()
            ]

        detailed_report = []
        recommendations = []
        seen_descriptions = set()
        sec_violations = 0
        clean_violations = 0
        quality_violations = 0
        confidences = []

        for item in snippets:
            code = item["code"]
            line = item["line_no"]
            scope_label = item.get("scope_label", "على المستوى العام")
            context_label = f"السطر {line} ({scope_label})"

            sec_res = SecurityAnalyzer.analyze_snippet(code)
            clean_res = CleanCodeAnalyzer.analyze_snippet(code)
            qual_res = ComplexityAnalyzer.analyze_snippet(code)

            issues = list(
                dict.fromkeys(
                    sec_res["issues"] + clean_res["issues"] + qual_res["issues"]
                )
            )
            category_key = "pass"
            if sec_res["has_issue"]:
                category_key = "security"
                sec_violations += 1
            elif qual_res["has_issue"]:
                category_key = "quality"
                quality_violations += 1
            elif clean_res["has_issue"]:
                category_key = "clean_code"
                clean_violations += 1

            predicted_category, predicted_label, confidence = (
                self.learning_loop.evaluate_and_learn(
                    code,
                    category_key,
                    "bad" if issues else "good",
                )
            )
            confidences.append(confidence)

            category_label = {
                "security": "Security",
                "quality": "Quality",
                "clean_code": "Clean Code",
                "pass": "Standard",
            }.get(category_key, "Standard")

            if issues:
                severity = "critical" if category_key == "security" else "warning"
                status = "حرج" if severity == "critical" else "تحذير"
                (
                    target_statement,
                    problem_description,
                    explanation_text,
                    recommendation_text,
                ) = self._build_rule_details(
                    issues, line, item.get("scope_name", "global"), code
                )
                if recommendation_text not in seen_descriptions:
                    recommendations.append(recommendation_text)
                    seen_descriptions.add(recommendation_text)
                label = status
            else:
                severity = "safe"
                status = "السطر سليم برمجياً"
                target_statement = "السطر سليم برمجياً"
                problem_description = "لا توجد تعليمات مخالفة في هذا السطر."
                explanation_text = "المقطع الحالي واضح وآمن."
                recommendation_text = "لا توجد توصيات إضافية."
                label = status

            detailed_report.append(
                {
                    "line": line,
                    "code": code,
                    "scope": scope_label,
                    "identifiers": item.get("identifiers", []),
                    "category": category_label,
                    "label": label,
                    "status": status,
                    "severity": severity,
                    "target_statement": target_statement,
                    "problem_description": problem_description,
                    "explanation_text": explanation_text,
                    "recommendation_text": recommendation_text,
                    "confidence": f"{confidence:.2%}",
                }
            )

        sec_score = max(0, 100 - (sec_violations * 25))
        clean_score = max(0, 100 - (clean_violations * 12))
        qual_score = max(0, 100 - (quality_violations * 14))
        overall_score = int(
            (sec_score * 0.45) + (clean_score * 0.30) + (qual_score * 0.25)
        )
        avg_conf = sum(confidences) / len(confidences) if confidences else 1.0

        self.audit_repo.save_log(
            filename,
            sec_score,
            clean_score,
            qual_score,
            overall_score,
            avg_conf,
        )

        return {
            "filename": filename,
            "scores": {
                "security": int(sec_score),
                "clean_code": int(clean_score),
                "quality": int(qual_score),
                "overall": int(overall_score),
            },
            "report": detailed_report,
            "avg_confidence": f"{avg_conf:.2%}",
            "summary": {
                "total_issues": len(
                    [
                        item
                        for item in detailed_report
                        if item["status"] != "السطر سليم برمجياً"
                    ]
                ),
                "recommendations": recommendations[:8],
            },
        }
