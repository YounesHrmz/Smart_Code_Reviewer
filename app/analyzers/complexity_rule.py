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
    def calculate_max_nesting(cls, code: str) -> int:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0

        max_depth = 0

        def visit(node, depth=0):
            nonlocal max_depth
            if isinstance(
                node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.ExceptHandler)
            ):
                max_depth = max(max_depth, depth + 1)
                for child in ast.iter_child_nodes(node):
                    visit(child, depth + 1)
            else:
                for child in ast.iter_child_nodes(node):
                    visit(child, depth)

        visit(tree, 0)
        return max_depth

    @classmethod
    def calculate_nesting_cause(cls, code: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return "تداخل بنيوي غير معروف"

        path = []
        best_path = []

        def visit(node, current):
            nonlocal best_path
            node_types = (
                ast.If,
                ast.For,
                ast.While,
                ast.Try,
                ast.With,
                ast.ExceptHandler,
            )
            if isinstance(node, node_types):
                current = current + [type(node)]
                if len(current) > len(best_path):
                    best_path = current
            for child in ast.iter_child_nodes(node):
                visit(child, current)

        visit(tree, [])

        if not best_path:
            return "تداخل بنيوي منخفض"

        type_names = []
        mapping = {
            ast.If: "شرطية",
            ast.For: "حلقة for",
            ast.While: "حلقة while",
            ast.Try: "كتلة try/except",
            ast.With: "كتلة with",
            ast.ExceptHandler: "معالج استثناء",
        }
        for node in best_path:
            type_names.append(mapping.get(node, "بنية تحكم"))

        unique_names = []
        for name in type_names:
            if not unique_names or unique_names[-1] != name:
                unique_names.append(name)

        if len(unique_names) == 1:
            return f"تداخل بنيوي نتيجة {unique_names[0]} متداخل"
        return f"تداخل بنيوي نتيجة {' ثم '.join(unique_names)}"

    @classmethod
    def analyze_snippet(cls, code: str) -> dict:
        issues = []
        severity = "safe"

        complexity = cls.calculate_cyclomatic_complexity(code)
        nesting_depth = cls.calculate_max_nesting(code)
        nesting_cause = cls.calculate_nesting_cause(code)

        # معايير التقييم الأكاديمية للتعقيد
        if complexity > 5:
            issues.append(
                f"المشكلة: تعقيد دوري مرتفع (الدرجة: {complexity}) يعني أن هناك العديد من المسارات المنطقية. "
                "التوصيات الهندسية: 1) قسم هذا الجزء إلى دوال أصغر ذات مسؤوليات واحدة. "
                "2) استخدم عبارات guard لتقليل التعقيدات الشرطية. "
                "3) أضف اختبارات وحدية تركز على كل فرع من فروع القرار."
            )
            severity = "warning"
            if complexity > 10:
                severity = "critical"

        # كشف التداخل البرمي العميق (Nested Structures)
        if nesting_depth >= 4:
            issues.append(
                f"المشكلة: تم اكتشاف {nesting_cause} بعمق {nesting_depth}، مما يزيد من صعوبة القراءة والصيانة. "
                "التوصيات الهندسية: 1) قسم المنطق إلى وحدات أو دوال منفصلة. "
                "2) استخدم استدعاءات مساعدة أو تصميم قائم على الأحداث لتقليل التداخل. "
                "3) احرص على أن يكون كل مستوى تحكم واضحًا ومحدودًا."
            )
            if severity != "critical":
                severity = "warning"
        elif code.count("    ") >= 4 or code.count("\t") >= 4:
            issues.append(
                f"المشكلة: استخدام مستويات متعددة من التراجع في الكود يمكن أن يشير إلى {nesting_cause} أو بنية معقدة. "
                "التوصيات الهندسية: 1) قلل التداخل بفصل الشرطيات إلى دوال مساعدة. "
                "2) راجع تصميم المستويات وتعامل مع الحالات بالتدرج."
            )
            if severity != "critical":
                severity = "warning"

        return {
            "complexity_score": complexity,
            "issues": issues,
            "severity": severity,
            "has_issue": len(issues) > 0,
        }
