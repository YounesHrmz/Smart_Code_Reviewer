import os

from flask import Flask, redirect, render_template, request, url_for

from app.config import Config
from app.database.connection import init_db
from app.services.review_service import CodeReviewService


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    Config.init_folders()
    init_db()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/review", methods=["GET", "POST"])
    def review():
        if request.method == "POST":
            uploaded_file = request.files.get("code_file")
            if uploaded_file and uploaded_file.filename:
                filename = uploaded_file.filename
                upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                uploaded_file.save(upload_path)

                with open(upload_path, "r", encoding="utf-8") as handle:
                    source_code = handle.read()

                review_service = CodeReviewService()
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
                    )

                return render_template(
                    "dashboard.html",
                    filename=filename,
                    scores=result.get("scores", {}),
                    confidence=result.get("avg_confidence", "0.00"),
                    report=result.get("report", []),
                )
        return redirect(url_for("index"))

    return app


app = create_app()
