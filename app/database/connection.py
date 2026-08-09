import csv
import sqlite3
import os
from app.config import Config


class DBConnection:
    """
    Context Manager لإدارة اتصالات قاعدة البيانات المحلية.
    يضمن فتح وقفل الاتصال وإرجاع السجلات على هيئة Dictionary مريح للتعامل.
    """

    def __init__(self):
        self.db_path = Config.DB_PATH

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        # جعل مخرجات القراءة تأتي بأسماء الأعمدة بدلاً من مصفوفة صماء
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()


def init_db():
    """
    تهيئة وإقلاع الجداول لأول مرة عند تشغيل النظام بناءً على ملف schema.sql
    """
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    with DBConnection() as cursor:
        cursor.executescript(sql_script)

        sample_csv = os.path.join(
            Config.BASE_DIR, "datasets", "sample_training_data.csv"
        )
        if os.path.exists(sample_csv):
            cursor.execute("DELETE FROM training_samples")
            with open(sample_csv, "r", encoding="utf-8", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                for record in reader:
                    confidence_value = record.get("confidence_score") or "0.0"
                    cursor.execute(
                        "INSERT OR IGNORE INTO training_samples (code_snippet, predicted_category, predicted_label, confidence_score) VALUES (?, ?, ?, ?)",
                        (
                            record["code_snippet"],
                            record["predicted_category"],
                            record["predicted_label"],
                            float(confidence_value),
                        ),
                    )
    print("✨ Local SQLite Database Architecture Initialized Successfully.")
