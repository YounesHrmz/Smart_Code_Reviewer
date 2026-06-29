import ast


class ASTParser:
    """
    المسؤول عن فحص الهيكل النحوي البرمجي لكود البايثون وعزل الكتل بدقة وضمان ملء الجدول.
    """

    def __init__(self, source_code: str):
        self.source_code = source_code
        try:
            self.tree = ast.parse(source_code)
        except SyntaxError:
            self.tree = None

    def is_valid(self) -> bool:
        return self.tree is not None

    def get_isolated_snippets(self) -> list:
        lines = self.source_code.splitlines()
        snippets = []

        if not self.tree:
            return [
                {"line_no": i + 1, "code": line.strip()}
                for i, line in enumerate(lines)
                if line.strip()
            ]

        for node in ast.walk(self.tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                    ast.Assign,
                    ast.Call,
                    ast.Expr,
                ),
            ):
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                if end and end <= len(lines):
                    snippet_text = "\n".join(lines[start - 1 : end]).strip()
                    if snippet_text and not any(
                        s["code"] == snippet_text for s in snippets
                    ):
                        snippets.append({"line_no": start, "code": snippet_text})

        if not snippets:
            for idx, line in enumerate(lines):
                if line.strip() and not line.strip().startswith("#"):
                    snippets.append({"line_no": idx + 1, "code": line.strip()})

        snippets.sort(key=lambda x: x["line_no"])
        return snippets

    def extract_structural_metrics(self) -> dict:
        if not self.tree:
            return {}

        metrics = {
            "num_functions": 0,
            "num_classes": 0,
            "num_imports": 0,
            "num_loops": 0,
            "num_conditions": 0,
            "num_comments": 0,
            "num_docstrings": 0,
            "max_nesting_depth": 0,
            "avg_function_length": 0,
        }

        function_lengths = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics["num_functions"] += 1
                function_lengths.append(len(node.body))
            elif isinstance(node, ast.ClassDef):
                metrics["num_classes"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics["num_imports"] += 1
            elif isinstance(node, (ast.For, ast.While)):
                metrics["num_loops"] += 1
            elif isinstance(node, ast.If):
                metrics["num_conditions"] += 1
            elif (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                metrics["num_docstrings"] += 1

        if function_lengths:
            metrics["avg_function_length"] = sum(function_lengths) / len(
                function_lengths
            )

        return metrics
