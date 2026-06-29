import os
from app.analyzers.ast_parser import ASTParser
from app.analyzers.security_rules import SecurityAnalyzer
from app.analyzers.clean_code_rule import CleanCodeAnalyzer
from app.analyzers.complexity_rule import ComplexityAnalyzer
from app.ml.self_learning import AutonomousLearningLoop
from app.repositories.audit_repository import AuditRepository


class CodeReviewService:
    """
    الخدمة المركزية لربط الفحص الاستاتيكي بنموذج التعلم الآلي وضمان تدفق الحلول الميدانية.
    """

    def __init__(self):
        self.learning_loop = AutonomousLearningLoop()
        self.audit_repo = AuditRepository()

    def process_file_analysis(self, filename: str, source_code: str) -> dict:
        parser = ASTParser(source_code)
        if not parser.is_valid():
            return {
                "error": "خطأ في بناء الجملة: الملف المرفوع ليس نصًّا بايثون صالحًا.",
                "summary": {
                    "total_issues": 0,
                    "recommendations": [],
                },
                "report": [],
            }

        snippets = parser.get_isolated_snippets()
        if not snippets:
            lines = source_code.splitlines()
            snippets = [
                {"line_no": idx + 1, "code": line.strip()}
                for idx, line in enumerate(lines)
                if line.strip()
            ]

        detailed_report = []
        sec_violations = 0
        clean_violations = 0
        quality_violations = 0
        confidences = []
        recommendations = []
        seen_descriptions = set()

        for item in snippets:
            code = item["code"]
            line = item["line_no"]

            sec_res = SecurityAnalyzer.analyze_snippet(code)
            clean_res = CleanCodeAnalyzer.analyze_snippet(code)
            qual_res = ComplexityAnalyzer.analyze_snippet(code)

            combined_issues = (
                sec_res["issues"] + clean_res["issues"] + qual_res["issues"]
            )
            fallback_cat = "clean_code"
            if sec_res["has_issue"]:
                fallback_cat = "security"
            elif qual_res["has_issue"]:
                fallback_cat = "quality"

            fallback_label = "bad" if combined_issues else "good"
            final_cat, final_label, confidence = self.learning_loop.evaluate_and_learn(
                code, fallback_cat, fallback_label
            )
            confidences.append(confidence)

            if final_label == "bad" or combined_issues:
                final_label = "مشكلة"
                if fallback_cat == "security":
                    sec_violations += 1
                elif fallback_cat == "clean_code":
                    clean_violations += 1
                elif fallback_cat == "quality":
                    quality_violations += 1
                severity = "critical" if fallback_cat == "security" else "warning"
                issue_text = (
                    " | ".join(combined_issues)
                    if combined_issues
                    else "تم اكتشاف بنية غير طبيعية بواسطة الذكاء المحلي، ويحتاج هذا الجزء إلى مراجعة هندسية فورية."
                )
                description = f"السطر {line}: {issue_text}"
                if description not in seen_descriptions:
                    recommendations.append(description)
                    seen_descriptions.add(description)
            else:
                final_label = "مقبول"
                severity = "safe"
                description = f"السطر {line}: هذا الجزء من الكود يتوافق مع معايير البنية المحلية ولا يحتاج إلى تحسينات فورية."

            category_label = (
                "أمن"
                if fallback_cat == "security"
                else (
                    "نظافة كود"
                    if fallback_cat == "clean_code"
                    else "جودة" if fallback_cat == "quality" else "قياسي"
                )
            )

            detailed_report.append(
                {
                    "line": line,
                    "code": code,
                    "category": category_label if final_label == "مشكلة" else "قياسي",
                    "label": final_label,
                    "confidence": f"{confidence:.2%}",
                    "severity": severity,
                    "description": description,
                }
            )

        sec_score = max(0, 100 - (sec_violations * 20))
        clean_score = max(0, 100 - (clean_violations * 10))
        qual_score = max(0, 100 - (quality_violations * 15))
        overall_score = (sec_score * 0.40) + (clean_score * 0.30) + (qual_score * 0.30)
        avg_conf = sum(confidences) / len(confidences) if confidences else 1.0

        self.audit_repo.save_log(
            filename, sec_score, clean_score, qual_score, overall_score, avg_conf
        )

        return {
            "filename": filename,
            "scores": {
                "security": int(sec_score),
                "clean_code": int(clean_score),
                "quality": int(qual_score),
                "overall": int(overall_score),
            },
            "report": detailed_report,
            "avg_confidence": f"{avg_conf:.2%}",
            "summary": {
                "total_issues": len(
                    [item for item in detailed_report if item["label"] == "مشكلة"]
                ),
                "recommendations": recommendations[:8],
            },
        }
