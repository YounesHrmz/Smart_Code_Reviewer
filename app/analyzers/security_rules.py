import ast
import re
from typing import Dict, List, Optional


class SecurityAnalyzer:
    """
    مستودع القواعد الأمنية الاستاتيكية لكشف الدوال الخطيرة وحقن البيانات والـ Hardcoded Secrets.
    """

    SECRET_PATTERNS = [
        r"(?i)(password|passwd|secret|token|api_key|aws_key|access_key)\s*=\s*[\'\"][^\'\"]+[\'\"]"
    ]

    DANGEROUS_CALLS = {
        "eval": "المشكلة: استخدام eval يعرض التطبيق لحقن كود ديناميكي. التوصيات: استخدم تعابير آمنة بدلا من تنفيذ النصوص.",
        "exec": "المشكلة: exec يسمح بتنفيذ تعليمات غير معروفة ضمن بيئة التشغيل. التوصيات: استخدم بدائل ثابتة وعزل التنفيذ.",
        "compile": "المشكلة: compile مع بيانات غير موثوقة قد تؤدي إلى تنفيذ كود ضار. التوصيات: تجنب توليد الكود من مدخلات المستخدم.",
        "os.system": "المشكلة: os.system ينفذ أوامر نظام خارجية ويمكن أن يسمح بحقن أوامر. التوصيات: استخدم واجهات نظام آمنة بدلا من shell.",
        "subprocess.call": "المشكلة: subprocess.call مع مدخلات غير موثوقة يمكن أن يفتح باب تنفيذ أوامر خارجي. التوصيات: استخدم قائمة معاملات واضحة ولا تمرر سلاسل shell.",
        "subprocess.Popen": "المشكلة: subprocess.Popen مع shell=True قد يعرض النظام لحقن الأوامر. التوصيات: استعمل shell=False ومرر arguments كقائمة.",
        "pickle.loads": "المشكلة: pickle.loads يعالج بيانات مهيأة قد تحتوي على أكواد خبيثة. التوصيات: استخدم تنسيقات آمنة مثل JSON أو protobuf.",
        "yaml.load": "المشكلة: yaml.load يحمل محتوى YAML غير موثوق. التوصيات: استبدله بـ yaml.safe_load واحصر المصادر الموثوقة.",
    }

    SQL_FUNCTIONS = {"execute", "executemany", "executescript"}
    COMMAND_FUNCTIONS = {"run", "call", "Popen", "check_output"}

    class _SecurityVisitor(ast.NodeVisitor):
        def __init__(self):
            self.issues: List[str] = []
            self.import_aliases: Dict[str, str] = {}
            self.imported_names: Dict[str, str] = {}

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                self.import_aliases[alias.asname or alias.name] = alias.name
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            module = node.module or ""
            for alias in node.names:
                imported_name = alias.asname or alias.name
                self.imported_names[imported_name] = (
                    f"{module}.{alias.name}" if module else alias.name
                )
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            call_name = self._resolve_call_name(node.func)
            if call_name:
                self._check_dangerous_call(call_name)
                self._check_sql_injection(node)
                self._check_command_injection(node)
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                name = self._resolve_target_name(target)
                if name and re.search(
                    r"(?i)password|passwd|secret|token|api_key|aws_key|access_key", name
                ):
                    if isinstance(node.value, ast.Constant) and isinstance(
                        node.value.value, str
                    ):
                        self.issues.append(
                            f"المشكلة: وجود قيمة حساسة مخزنة في الكود تحت اسم {name}. التوصيات: انقلها إلى متغيرات بيئية أو مدير أسرار."
                        )
            self.generic_visit(node)

        def _resolve_call_name(self, node: ast.AST) -> Optional[str]:
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Attribute):
                parent_name = self._resolve_call_name(node.value)
                return f"{parent_name}.{node.attr}" if parent_name else node.attr
            return None

        def _resolve_target_name(self, node: ast.AST) -> Optional[str]:
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Attribute):
                return node.attr
            return None

        def _normalize_call(self, call_name: str) -> str:
            parts = call_name.split(".")
            if parts[0] in self.import_aliases:
                parts[0] = self.import_aliases[parts[0]]
            if parts[0] in self.imported_names:
                parts[0] = self.imported_names[parts[0]]
            return ".".join(parts)

        def _check_dangerous_call(self, call_name: str) -> None:
            normalized = self._normalize_call(call_name)
            if normalized in SecurityAnalyzer.DANGEROUS_CALLS:
                self.issues.append(SecurityAnalyzer.DANGEROUS_CALLS[normalized])
            elif call_name in SecurityAnalyzer.DANGEROUS_CALLS:
                self.issues.append(SecurityAnalyzer.DANGEROUS_CALLS[call_name])

        def _check_sql_injection(self, node: ast.Call) -> None:
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in SecurityAnalyzer.SQL_FUNCTIONS
            ):
                for arg in node.args:
                    if self._is_concat_with_keywords(
                        arg, ["select", "insert", "update", "delete", "where"]
                    ):
                        self.issues.append(
                            "المشكلة: بناء استعلام SQL عن طريق ربط سلاسل نصية قد يعرض النظام لحقن بيانات. التوصيات: استخدم استعلامات parameterized وتجنب تجميع السلاسل."
                        )

        def _check_command_injection(self, node: ast.Call) -> None:
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in SecurityAnalyzer.COMMAND_FUNCTIONS
            ):
                if any(
                    self._is_concat_with_keywords(arg, ["ping", "rm", "ls", "curl"])
                    for arg in node.args
                ):
                    self.issues.append(
                        "المشكلة: قد يكون هناك حقن أوامر عند تمرير بناء سلسلة غير آمن إلى دالة أوامر النظام. التوصيات: استعمل قائمة وسائط وتعطيل shell."
                    )

        def _is_concat_with_keywords(self, node: ast.AST, keywords: List[str]) -> bool:
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                parts = self._flatten_concat(node)
                full = "".join(part for part in parts if isinstance(part, str)).lower()
                return any(keyword in full for keyword in keywords)
            return False

        def _flatten_concat(self, node: ast.AST) -> List[str]:
            parts: List[str] = []
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                parts.extend(self._flatten_concat(node.left))
                parts.extend(self._flatten_concat(node.right))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                parts.append(node.value)
            return parts

    @classmethod
    def analyze_snippet(cls, code: str) -> dict:
        issues: List[str] = []
        severity = "safe"

        try:
            tree = ast.parse(code)
            visitor = cls._SecurityVisitor()
            visitor.visit(tree)
            issues.extend(visitor.issues)
        except SyntaxError:
            pass

        if not issues:
            for pattern in cls.SECRET_PATTERNS:
                match = re.search(pattern, code)
                if match:
                    secret_name = match.group(1) if match.groups() else "secret"
                    issues.append(
                        f"المشكلة: وجود قيمة حساسة مخزنة في الكود تحت اسم {secret_name}. التوصيات: انقلها إلى متغيرات بيئية أو مدير أسرار."
                    )
                    break

        if issues:
            severity = "critical"

        return {"issues": issues, "severity": severity, "has_issue": len(issues) > 0}
