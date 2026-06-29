import re


class CleanCodeAnalyzer:
    """
    مسؤول عن فحص معايير نظافة الكود (Clean Code Styles) وجودة التسميات وجودة التوثيق.
    """

    # كشف الأسماء المبهمة والقصيرة جداً مثل x, y, tmp
    BAD_NAMES = r"\b(x|y|z|tmp|temp|data|val|var|foo|bar)\b"

    @classmethod
    def analyze_snippet(cls, code: str) -> dict:
        issues = []
        severity = "safe"

        # 1. فحص جودة التسميات (Naming Quality)
        # نفحص الأسطر التي تحتوي على تعريف دوال أو تعيين متغيرات
        if "=" in code or "def " in code:
            matches = re.findall(cls.BAD_NAMES, code)
            if matches:
                distinct_matches = list(set(matches))
                issues.append(
                    f"المشكلة: استخدام أسماء غير وصفية أو غامضة مثل {distinct_matches}. التوصية الهندسية: استبدلها بأسماء أوضح تعبر عن الغرض وتحسن قراءة الكود."
                )
                severity = "warning"

        # 2. فحص غياب التنسيق البرمجي الأساسي (مثل غياب الفراغات أو دمج التعليمات بفاصلة منقوطة)
        if ";" in code and not code.strip().startswith("#"):
            issues.append(
                "المشكلة: دمج أكثر من عبارة في سطر واحد باستخدام ';'. التوصية الهندسية: افصل العبارات على سطور منفصلة وطبق أسلوب PEP 8."
            )
            severity = "warning"

        return {"issues": issues, "severity": severity, "has_issue": len(issues) > 0}
