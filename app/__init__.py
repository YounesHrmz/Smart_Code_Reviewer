import html
import os
import json
from flask import Flask, redirect, render_template, request, url_for, Response

from app.config import Config
from app.database.connection import init_db
from app.export.pdf_exporter import PDFExporter
from app.services.review_service import CodeReviewService


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    Config.init_folders()
    # Ensure rule templates file exists so operators can edit rules without code changes
    try:
        from app.services.review_service import (
            save_default_rule_templates,
            reload_rule_templates,
        )

        save_default_rule_templates()
        reload_rule_templates()
    except Exception:
        pass
    init_db()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/review", methods=["GET", "POST"])
    def review():
        if request.method == "POST":
            review_service = CodeReviewService()
            source_code = ""
            filename = "analysis.py"
            uploaded_files = request.files.getlist("code_files")

            if uploaded_files:
                results = []
                for upload in uploaded_files:
                    if upload and upload.filename:
                        upload_path = os.path.join(
                            Config.UPLOAD_FOLDER, upload.filename
                        )
                        upload.save(upload_path)
                        with open(upload_path, "r", encoding="utf-8") as handle:
                            source_code = handle.read()
                        result = review_service.process_file_analysis(
                            upload.filename, source_code
                        )
                        results.append(result)

                if results:
                    aggregate_scores = {
                        "overall": int(
                            sum(
                                item.get("scores", {}).get("overall", 0)
                                for item in results
                            )
                            / len(results)
                        ),
                        "security": int(
                            sum(
                                item.get("scores", {}).get("security", 0)
                                for item in results
                            )
                            / len(results)
                        ),
                        "clean_code": int(
                            sum(
                                item.get("scores", {}).get("clean_code", 0)
                                for item in results
                            )
                            / len(results)
                        ),
                        "quality": int(
                            sum(
                                item.get("scores", {}).get("quality", 0)
                                for item in results
                            )
                            / len(results)
                        ),
                    }
                    aggregated_report = []
                    aggregated_recommendations = []
                    total_issues = 0
                    for item in results:
                        aggregated_report.extend(item.get("report", []))
                        aggregated_recommendations.extend(
                            item.get("summary", {}).get("recommendations", [])
                        )
                        total_issues += item.get("summary", {}).get("total_issues", 0)
                    return render_template(
                        "dashboard.html",
                        filename="multi_file_analysis",
                        scores=aggregate_scores,
                        confidence="0.00",
                        report=aggregated_report,
                        summary={
                            "total_issues": total_issues,
                            "recommendations": aggregated_recommendations[:8],
                        },
                    )

            uploaded_file = request.files.get("code_file")
            if uploaded_file and uploaded_file.filename:
                filename = uploaded_file.filename
                upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                uploaded_file.save(upload_path)
                with open(upload_path, "r", encoding="utf-8") as handle:
                    source_code = handle.read()
                result = review_service.process_file_analysis(filename, source_code)
                if "error" in result:
                    return render_template(
                        "dashboard.html",
                        filename=filename,
                        scores={
                            "overall": 0,
                            "security": 0,
                            "clean_code": 0,
                            "quality": 0,
                        },
                        confidence="0.00",
                        report=[],
                        summary={"total_issues": 0, "recommendations": []},
                    )
                return render_template(
                    "dashboard.html",
                    filename=filename,
                    scores=result.get("scores", {}),
                    confidence=result.get("avg_confidence", "0.00"),
                    report=result.get("report", []),
                    summary=result.get(
                        "summary", {"total_issues": 0, "recommendations": []}
                    ),
                )

            code_text = request.form.get("code_text", "")
            if code_text.strip():
                result = review_service.process_file_analysis(filename, code_text)
                return render_template(
                    "dashboard.html",
                    filename=filename,
                    scores=result.get("scores", {}),
                    confidence=result.get("avg_confidence", "0.00"),
                    report=result.get("report", []),
                    summary=result.get(
                        "summary", {"total_issues": 0, "recommendations": []}
                    ),
                )
        return redirect(url_for("index"))

    @app.route("/export/<path:filename>/<export_type>")
    def export_report(filename, export_type):
        if export_type not in {"html", "pdf", "json"}:
            return redirect(url_for("index"))

        base_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        if not os.path.exists(base_path):
            return redirect(url_for("index"))

        with open(base_path, "r", encoding="utf-8") as handle:
            source_code = handle.read()
        result = CodeReviewService().process_file_analysis(filename, source_code)

        if export_type == "json":
            payload = json.dumps(result, ensure_ascii=False, indent=2)
            return Response(
                payload,
                mimetype="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}.json"
                },
            )

        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if export_type == "html":
            html_content = f'<html><head><meta charset="utf-8"></head><body><h1>Code Review Report</h1><pre>{html.escape(payload)}</pre></body></html>'
            return Response(
                html_content,
                mimetype="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}.html"
                },
            )

        pdf_bytes = PDFExporter.generate_pdf_bytes(filename, result)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}.pdf"},
        )

    return app


app = create_app()
