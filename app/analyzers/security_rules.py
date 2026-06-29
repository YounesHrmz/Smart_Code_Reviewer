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
                    f"المشكلة: استخدام دالة خطيرة [{func}] قد يزيد من خطر تنفيذ أوامر غير مرغوب فيها. التوصيات الهندسية: 1) استبدلها بوسيلة آمنة أو بديلة. 2) احجب السلوك الحساس داخل طبقة منفصلة. 3) أضف التحقق من المدخلات قبل أي تنفيذ."
                )
                severity = "critical"

        # 2. كشف مخاطر حقن الاستعلامات (SQL / Command Injection Risks)
        if ("SELECT" in code or "INSERT" in code or "WHERE" in code) and "+" in code:
            issues.append(
                "المشكلة: احتمال حقن SQL عبر ربط السلاسل غير الآمن. التوصيات الهندسية: 1) استخدم معايير جاهزة مثل parameterized queries. 2) تجنب الربط المباشر للسلاسل. 3) أضف اختبارات أمنية لحقن الإدخال."
            )
            severity = "critical"

        if ("ping" in code or "rm" in code or "ls" in code) and "+" in code:
            issues.append(
                "المشكلة: احتمال حقن أوامر النظام عبر ربط السلاسل غير الآمن. التوصيات الهندسية: 1) تجنب تنفيذ الأوامر مباشرة. 2) قلّل الاعتماد على المدخلات غير الموثوقة. 3) استخدم طبقة مسار آمنة مع التحقق من الصلاحيات."
            )
            severity = "critical"

        # 3. كشف الـ Hardcoded Secrets
        for pattern in cls.SECRET_PATTERNS:
            if re.search(pattern, code):
                issues.append(
                    "المشكلة: وجود مفاتيح أو توكنات حساسة مضمّنة مباشرة داخل الكود. التوصيات الهندسية: 1) انقلها إلى متغيرات بيئية. 2) استخدم مدير أسرار آمن. 3) أضف Rotation Policies وتقييد الوصول إلى هذه المفاتيح."
                )
                severity = "critical"

        return {"issues": issues, "severity": severity, "has_issue": len(issues) > 0}
