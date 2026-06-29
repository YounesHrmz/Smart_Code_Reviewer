import re


class SecurityAnalyzer:
    """
    مستودع القواعد الأمنية الاستاتيكية لكشف الدوال الخطيرة وحقن البيانات والـ Hardcoded Secrets.
    """

    DANGEROUS_FUNCTIONS = [
        "eval",
        "exec",
        "compile",
        "os.system",
        "subprocess.call",
        "subprocess.Popen",
        "pickle.loads",
        "yaml.load",
    ]

    # تعبيرات منتظمة لاكتشاف تسريب المفاتيح والتوكنز السرية بشكل صارم
    SECRET_PATTERNS = [
        r'(?i)(password|passwd|secret|token|api_key|aws_key|access_key)\s*=\s*[\'"][^\'"]+[\'"]'
    ]

    @classmethod
    def analyze_snippet(cls, code: str) -> dict:
        """
        فحص العينة برمجياً وإرجاع المشاكل الأمنية المكتشفة مع التوصيات
        """
        issues = []
        severity = "safe"

        # 1. كشف الدوال الخطيرة (Dangerous Functions)
        for func in cls.DANGEROUS_FUNCTIONS:
            if func in code:
                issues.append(
                    f"المشكلة: استخدام دالة خطيرة [{func}] قد يزيد من خطر تنفيذ أوامر غير مرغوب فيها. التوصية الهندسية: استبدلها بوسيلة آمنة أو احجبها في طبقة منفصلة مع التحقق من الإدخال."
                )
                severity = "critical"

        # 2. كشف مخاطر حقن الاستعلامات (SQL / Command Injection Risks)
        if ("SELECT" in code or "INSERT" in code or "WHERE" in code) and "+" in code:
            issues.append(
                "المشكلة: احتمال حقن SQL عبر ربط السلاسل غير الآمن. التوصية الهندسية: استخدم معايير جاهزة أو معاملات مخصصة بدل الربط المباشر."
            )
            severity = "critical"

        if ("ping" in code or "rm" in code or "ls" in code) and "+" in code:
            issues.append(
                "المشكلة: احتمال حقن أوامر النظام عبر ربط السلاسل غير الآمن. التوصية الهندسية: تجنب تنفيذ الأوامر مباشرة وقلّل الاعتماد على المدخلات غير الموثوقة."
            )
            severity = "critical"

        # 3. كشف الـ Hardcoded Secrets
        for pattern in cls.SECRET_PATTERNS:
            if re.search(pattern, code):
                issues.append(
                    "المشكلة: وجود مفاتيح أو توكنات حساسة مضمّنة مباشرة داخل الكود. التوصية الهندسية: انقلها إلى متغيرات بيئية أو مدير أسرار آمن."
                )
                severity = "critical"

        return {"issues": issues, "severity": severity, "has_issue": len(issues) > 0}
