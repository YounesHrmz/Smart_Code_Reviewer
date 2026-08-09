import os
from app.analyzers.ast_parser import ASTParser
from app.analyzers.clean_code_rule import CleanCodeAnalyzer
from app.analyzers.complexity_rule import ComplexityAnalyzer
from app.analyzers.security_rules import SecurityAnalyzer
from app.ml.self_learning import AutonomousLearningLoop
from app.repositories.audit_repository import AuditRepository


class CodeReviewService:
    """
    خدمة المراجعة التي تجمع نتائج تحليل AST والقواعد الثابتة مع دورة تعلم آلي محلية.
    """

    def __init__(self):
        self.learning_loop = AutonomousLearningLoop()
        self.audit_repo = AuditRepository()

    def process_file_analysis(self, filename: str, source_code: str) -> dict:
        parser = ASTParser(source_code)
        if not parser.is_valid():
            return {
                "error": "خطأ في بناء الجملة: الملف المرسل ليس بايثون صالحًا.",
                "summary": {"total_issues": 0, "recommendations": []},
                "report": [],
            }

        snippets = parser.get_snippets()
        if not snippets:
            snippets = [
                {
                    "line_no": idx + 1,
                    "code": line.strip(),
                    "scope_label": "على المستوى العام",
                    "node_type": "سطر",
                    "identifiers": [],
                }
                for idx, line in enumerate(source_code.splitlines())
                if line.strip()
            ]

        detailed_report = []
        recommendations = []
        seen_descriptions = set()
        sec_violations = 0
        clean_violations = 0
        quality_violations = 0
        confidences = []

        for item in snippets:
            code = item["code"]
            line = item["line_no"]
            scope_label = item.get("scope_label", "على المستوى العام")
            context_label = f"السطر {line} ({scope_label})"

            sec_res = SecurityAnalyzer.analyze_snippet(code)
            clean_res = CleanCodeAnalyzer.analyze_snippet(code)
            qual_res = ComplexityAnalyzer.analyze_snippet(code)

            issues = list(
                dict.fromkeys(
                    sec_res["issues"] + clean_res["issues"] + qual_res["issues"]
                )
            )
            category_key = "pass"
            if sec_res["has_issue"]:
                category_key = "security"
                sec_violations += 1
            elif qual_res["has_issue"]:
                category_key = "quality"
                quality_violations += 1
            elif clean_res["has_issue"]:
                category_key = "clean_code"
                clean_violations += 1

            predicted_category, predicted_label, confidence = (
                self.learning_loop.evaluate_and_learn(
                    code,
                    category_key,
                    "bad" if issues else "good",
                )
            )
            confidences.append(confidence)

            category_label = {
                "security": "أمن",
                "quality": "جودة",
                "clean_code": "نظافة كود",
                "pass": "قياسي",
            }.get(category_key, "قياسي")

            if issues:
                severity = "critical" if category_key == "security" else "warning"
                description = " | ".join(issues)
                if description not in seen_descriptions:
                    recommendations.append(f"{context_label}: {description}")
                    seen_descriptions.add(description)
                label = "مشكلة"
            else:
                severity = "safe"
                description = ""
                label = "مقبول"

            detailed_report.append(
                {
                    "line": line,
                    "code": code,
                    "scope": scope_label,
                    "identifiers": item.get("identifiers", []),
                    "category": category_label,
                    "label": label,
                    "status": "issue" if issues else "pass",
                    "severity": severity,
                    "description": description,
                    "confidence": f"{confidence:.2%}",
                }
            )

        sec_score = max(0, 100 - (sec_violations * 25))
        clean_score = max(0, 100 - (clean_violations * 12))
        qual_score = max(0, 100 - (quality_violations * 14))
        overall_score = int(
            (sec_score * 0.45) + (clean_score * 0.30) + (qual_score * 0.25)
        )
        avg_conf = sum(confidences) / len(confidences) if confidences else 1.0

        self.audit_repo.save_log(
            filename,
            sec_score,
            clean_score,
            qual_score,
            overall_score,
            avg_conf,
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
                    [item for item in detailed_report if item["status"] == "issue"]
                ),
                "recommendations": recommendations[:8],
            },
        }
