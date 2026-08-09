import ast
import tokenize
from io import StringIO
from typing import Any, Dict, List, Optional


class ASTParser:
    """
    يحلل الشيفرة المصدرية إلى مقاطع AST مع سياق دقيق لكل عنصر.
    يوفر اسم المجال، نوع العقدة، مجموعة المعرفات، والمقطع البرمجي لكل عنصر.
    """

    ANALYSIS_TYPES = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Assign,
        ast.AugAssign,
        ast.Call,
        ast.Import,
        ast.ImportFrom,
        ast.With,
        ast.If,
        ast.For,
        ast.While,
        ast.Try,
    )

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.tree: Optional[ast.AST] = None
        self.parent_map: Dict[ast.AST, ast.AST] = {}
        try:
            self.tree = ast.parse(source_code)
            self._build_parent_map()
        except SyntaxError:
            self.tree = None

    def _build_parent_map(self) -> None:
        assert self.tree is not None
        for parent in ast.walk(self.tree):
            for child in ast.iter_child_nodes(parent):
                self.parent_map[child] = parent

    def is_valid(self) -> bool:
        return self.tree is not None

    def _get_scope_name(self, node: ast.AST) -> str:
        current = node
        while current is not None:
            if isinstance(
                current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                return current.name
            current = self.parent_map.get(current)
        return "global"

    def _resolve_call_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = self._resolve_call_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return "<unknown>"

    def _collect_identifiers(self, node: ast.AST) -> List[str]:
        identifiers: List[str] = []

        def visit(child: ast.AST) -> None:
            if isinstance(child, ast.Name):
                identifiers.append(child.id)
            elif isinstance(child, ast.Attribute):
                identifiers.append(child.attr)
            for grandchild in ast.iter_child_nodes(child):
                visit(grandchild)

        visit(node)
        return sorted(set(identifiers))

    def get_snippets(self) -> List[Dict[str, Any]]:
        if not self.tree:
            return [
                {
                    "line_no": idx + 1,
                    "code": line.strip(),
                    "scope_name": "global",
                    "scope_label": "على المستوى العام",
                    "node_type": "Line",
                    "identifiers": [],
                }
                for idx, line in enumerate(self.lines)
                if line.strip()
            ]

        snippets: List[Dict[str, Any]] = []
        seen = set()

        for node in ast.walk(self.tree):
            if isinstance(node, self.ANALYSIS_TYPES) and getattr(node, "lineno", None):
                start = getattr(node, "lineno", None)
                end = getattr(node, "end_lineno", start)
                code = ast.get_source_segment(self.source_code, node)
                if not code and start is not None:
                    snippet_lines = self.lines[start - 1 : end]
                    code = "\n".join(snippet_lines).strip()
                if not code:
                    continue

                key = (start, end, type(node).__name__, code)
                if key in seen:
                    continue
                seen.add(key)

                scope_name = self._get_scope_name(node)
                scope_label = (
                    f"داخل '{scope_name}'"
                    if scope_name != "global"
                    else "على المستوى العام"
                )
                identifiers = self._collect_identifiers(node)

                snippets.append(
                    {
                        "line_no": start,
                        "code": code,
                        "scope_name": scope_name,
                        "scope_label": scope_label,
                        "node_type": type(node).__name__,
                        "identifiers": identifiers,
                    }
                )

        if not snippets:
            return [
                {
                    "line_no": idx + 1,
                    "code": line.strip(),
                    "scope_name": "global",
                    "scope_label": "على المستوى العام",
                    "node_type": "Line",
                    "identifiers": [],
                }
                for idx, line in enumerate(self.lines)
                if line.strip()
            ]

        snippets.sort(key=lambda item: item["line_no"])
        return snippets

    def extract_structural_metrics(self) -> Dict[str, Any]:
        if not self.tree:
            return {}

        metrics = {
            "num_functions": 0,
            "num_classes": 0,
            "num_imports": 0,
            "num_loops": 0,
            "num_conditions": 0,
            "num_docstrings": 0,
            "num_comments": 0,
            "max_nesting_depth": 0,
            "avg_function_length": 0,
        }

        function_lengths: List[int] = []
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

        try:
            token_generator = tokenize.generate_tokens(
                StringIO(self.source_code).readline
            )
            metrics["num_comments"] = sum(
                1 for token in token_generator if token.type == tokenize.COMMENT
            )
        except tokenize.TokenError:
            metrics["num_comments"] = 0

        max_depth = 0

        def visit(node: ast.AST, depth: int = 0) -> None:
            nonlocal max_depth
            if isinstance(
                node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.ExceptHandler)
            ):
                depth += 1
                max_depth = max(max_depth, depth)
            for child in ast.iter_child_nodes(node):
                visit(child, depth)

        visit(self.tree, 0)
        metrics["max_nesting_depth"] = max_depth
        return metrics
