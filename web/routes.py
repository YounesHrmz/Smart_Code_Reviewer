import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from core.parser import extract_code_features
from core.model_trainer import predict_code_snippet, train_model

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "web", "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/review", methods=["POST"])
def review_code():
    if "code_file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["code_file"]
    if file.filename == "":
        return redirect(url_for("index"))

    # حفظ الملف المرفوع مؤقتاً
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # 1. تفكيك الكود عبر الـ AST Parser
    snippets = extract_code_features(file_path)

    if isinstance(snippets, dict) and "error" in snippets:
        return f"Error: {snippets['error']}"

    detailed_report = []
    sec_issues = 0
    clean_issues = 0
    qual_issues = 0
    auto_added_count = 0

    # 2. تمرير العينات البرمجية الملوثة للمودل للتنبؤ وحساب الثقة
    for snip in snippets:
        category, label, confidence = predict_code_snippet(snip["code"])

        if label == "bad":
            if category == "security":
                sec_issues += 1
            elif category == "clean_code":
                clean_issues += 1
            elif category == "quality":
                qual_issues += 1

        # إضافة البيانات للتقرير
        detailed_report.append(
            {
                "line": snip["line_no"],
                "code": snip["code"],
                "category": category,
                "label": label,
                "confidence": f"{confidence:.2%}",
            }
        )

        # --- ميزة التطور الذاتي الصامت للأتمتة ---
        # إذا كانت الثقة أعلى من العتبة المحددة (مثلاً 65% لتتناسب مع حجم الداتا سيت الحالي)
        if confidence >= 0.65:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # التأكد من عدم تكرار العينة في قاعدة البيانات
            cursor.execute(
                "SELECT id FROM dataset WHERE code_snippet = ?", (snip["code"],)
            )
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO dataset (code_snippet, category, label, description)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        snip["code"],
                        category,
                        label,
                        "تمت إضافتها تلقائياً عبر ميزة التعلم المستمر وثقة المودل العالية",
                    ),
                )
                conn.commit()
                auto_added_count += 1
            conn.close()

    # إعادة تدريب المودل تلقائياً في الخلفية إذا تم حقن بيانات جديدة لتحديث ذكائه فوراً
    if auto_added_count > 0:
        train_model()

    # حساب التقييمات الرقمية النهائية لإظهارها على الواجهة
    total_elements = len(snippets) if len(snippets) > 0 else 1
    scores = {
        "security": max(0, 100 - (sec_issues * 25)),
        "clean_code": max(0, 100 - (clean_issues * 15)),
        "quality": max(0, 100 - (qual_issues * 20)),
        "auto_added": auto_added_count,
    }

    # تسجيل الفحص في الـ Audit Logs
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO audit_logs (filename, security_score, clean_code_score, quality_score)
        VALUES (?, ?, ?, ?)
    """,
        (file.filename, scores["security"], scores["clean_code"], scores["quality"]),
    )
    conn.commit()
    conn.close()

    # قراءة النص بالكامل لعرضه على الواجهة مع التقرير
    with open(file_path, "r", encoding="utf-8") as f:
        full_code = f.read()

    return render_template(
        "dashboard.html",
        scores=scores,
        report=detailed_report,
        full_code=full_code,
        filename=file.filename,
    )


if __name__ == "__main__":
    app.run(debug=True)
