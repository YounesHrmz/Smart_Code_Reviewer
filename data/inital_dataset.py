import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dataset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_snippet TEXT NOT NULL,
            category TEXT NOT NULL,       -- 'security', 'clean_code', 'quality'
            label TEXT NOT NULL,          -- 'good' (سليم) أو 'bad' (يحتوي مخالفة)
            description TEXT              -- شرح المخالفة البرمجية
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            security_score REAL,
            clean_code_score REAL,
            quality_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM dataset")
    if cursor.fetchone()[0] == 0:
        initial_samples = [
            (
                "query = 'SELECT * FROM users WHERE id = ' + user_input",
                "security",
                "bad",
                "SQL injection vulnerability from direct string concatenation",
            ),
            (
                "cursor.execute('SELECT * FROM users WHERE id = ?', (user_input,))",
                "security",
                "good",
                "Secure code using prepared statements to prevent SQL injection",
            ),
            (
                "password = 'super_secret_password_123'",
                "security",
                "bad",
                "Hardcoded secrets - passwords and keys stored directly in code",
            ),
            (
                "eval(user_data)",
                "security",
                "bad",
                "Using eval is dangerous as it allows dynamic code execution",
            ),
            (
                "def x(a, b):\n    return a+b",
                "clean_code",
                "bad",
                "Ambiguous variable and function names that don't express purpose",
            ),
            (
                "def calculate_total_price(item_price, tax_rate):\n    return item_price + tax_rate",
                "clean_code",
                "good",
                "Clear and expressive naming following PEP 8 standards",
            ),
            (
                "import os, sys, time, json",
                "clean_code",
                "bad",
                "Multiple imports on one line violates clean code formatting standards",
            ),
            (
                "for i in range(10):\n    for j in range(5):\n        for k in range(3):\n            print(i, j, k)",
                "quality",
                "bad",
                "High cyclomatic complexity from deeply nested loops",
            ),
            (
                "def process_data(data):\n    # دالة بسيطة تؤدي غرضاً واحداً\n    return [d * 2 for d in data]",
                "quality",
                "good",
                "كود ذو جودة عالية، تعقيد منخفض، ويؤدي وظيفة واحدة محددة",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO dataset (code_snippet, category, label, description)
            VALUES (?, ?, ?, ?)
        """,
            initial_samples,
        )
        conn.commit()
        print("Successfully initialized database with benchmark samples.")
    else:
        print("Database already exists and contains data.")

    conn.close()


if __name__ == "__main__":
    init_db()
