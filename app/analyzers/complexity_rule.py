import ast


class ComplexityAnalyzer:
    """
    محرك مخصص لحساب التعقيد الدوري (Cyclomatic Complexity) برياضيات اتخاذ القرار،
    وكشف كتل التداخل العميق (Deep Nesting).
    """

    @classmethod
    def calculate_cyclomatic_complexity(cls, code: str) -> int:
        """
        حساب التعقيد الدوري بناءً على عدد التفرعات (M = E - N + 2P) مبسطاً:
        يبدأ من 1، وكل أداة شرط، حلقة تكرار، أو استثناء تزيد التعقيد بمقدار 1.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 1

        complexity = 1
        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.And,
                    ast.Or,
                    ast.Try,
                    ast.ExceptHandler,
                ),
            ):
                complexity += 1
        return complexity

    @classmethod
    def analyze_snippet(cls, code: str) -> dict:
        issues = []
        severity = "safe"

        complexity = cls.calculate_cyclomatic_complexity(code)

        # معايير التقييم الأكاديمية للتعقيد
        if complexity > 5:
            issues.append(
                f"المشكلة: تعقيد دوري مرتفع (الدرجة: {complexity}) مما يجعل هذا الجزء صعب الاختبار والصيانة. التوصية الهندسية: قسم المنطق إلى دوال أو وحدات أصغر."
            )
            severity = "warning"
            if complexity > 10:
                severity = "critical"

        # كشف التداخل البرمي العميق (Nested Structures)
        if code.count("    ") >= 4 or code.count("\t") >= 4:
            issues.append(
                "المشكلة: تم اكتشاف تداخل عميق في البنية. التوصية الهندسية: قسم هذا المنطق إلى دوال أو وحدات منفصلة لتسهيل الفهم والصيانة."
            )
            if severity != "critical":
                severity = "warning"

        return {
            "complexity_score": complexity,
            "issues": issues,
            "severity": severity,
            "has_issue": len(issues) > 0,
        }
