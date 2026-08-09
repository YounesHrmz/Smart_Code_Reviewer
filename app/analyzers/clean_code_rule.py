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
        if "=" in code or "def " in code:
            matches = re.findall(cls.BAD_NAMES, code)
            if matches:
                distinct_matches = sorted(set(matches))
                variable_list = "، ".join(distinct_matches)
                issues.append(
                    f"المشكلة: استخدام أسماء مبهمة أو مؤقتة مثل {variable_list}. "
                    "التوصيات الهندسية: 1) استبدلها بأسماء تعكس المحتوى أو الغرض. "
                    "2) اعتمد أسماء واضحة وثابتة عبر المشروع. "
                    "3) تجنّب الاختصارات غير المفهومة في السياقات الحرجة."
                )
                severity = "warning"

        # 2. فحص غياب التنسيق البرمجي الأساسي (مثل غياب الفراغات أو دمج التعليمات بفاصلة منقوطة)
        if ";" in code and not code.strip().startswith("#"):
            count = code.count(";")
            issues.append(
                f"المشكلة: وجود {count} فاصلة منقوطة داخل سطر واحد مما يقلل من وضوح الكود. "
                "التوصيات الهندسية: 1) افصل العبارات على أسطر مستقلة. "
                "2) حافظ على تعبير واحد لكل سطر لتسهيل الصيانة. "
                "3) اتبع قواعد تنسيق أسلوب Python القياسية."
            )
            severity = "warning"

        return {"issues": issues, "severity": severity, "has_issue": len(issues) > 0}
