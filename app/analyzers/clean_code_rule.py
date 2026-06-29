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
                    f"المشكلة: استخدام أسماء غير وصفية أو غامضة مثل {distinct_matches}. التوصيات الهندسية: 1) استبدلها بأسماء أوضح تعبر عن الغرض. 2) استخدم اصطلاحات تسميّة ثابتة مثل snake_case. 3) اجعل الاسم يوضح الدور والوظيفة دون الحاجة إلى تعليق."
                )
                severity = "warning"

        # 2. فحص غياب التنسيق البرمجي الأساسي (مثل غياب الفراغات أو دمج التعليمات بفاصلة منقوطة)
        if ";" in code and not code.strip().startswith("#"):
            issues.append(
                "المشكلة: دمج أكثر من عبارة في سطر واحد باستخدام ';'. التوصيات الهندسية: 1) افصل العبارات على سطور منفصلة. 2) حافظ على سطر واحد لكل مهمة واضحة. 3) اتبع أسلوب PEP 8 لتحسين القراءة والصيانة."
            )
            severity = "warning"

        return {"issues": issues, "severity": severity, "has_issue": len(issues) > 0}
