-- جدول المستخدمين (تأسيس أمني مرن قابل للتوسيع لاحقاً)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول سجلات الفحص والتقارير (Audit Logs)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    security_score REAL NOT NULL,
    clean_code_score REAL NOT NULL,
    quality_score REAL NOT NULL,
    overall_score REAL NOT NULL,
    confidence_average REAL NOT NULL
);

-- جدول عينات التدريب للتطور الذاتي المستقل (Training Samples)
CREATE TABLE IF NOT EXISTS training_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_snippet TEXT NOT NULL UNIQUE, -- حماية من الـ Duplicate Samples لتجنب التسمم
    predicted_category VARCHAR(50) NOT NULL,
    predicted_label VARCHAR(10) NOT NULL, -- 'good' أو 'bad'
    confidence_score REAL NOT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول سجلات وعمليات إعادة التدريب التلقائي (Retraining Logs)
CREATE TABLE IF NOT EXISTS retraining_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    previous_accuracy REAL,
    new_accuracy REAL,
    samples_count INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL -- 'SUCCESS_UPGRADED' أو 'FAILED_ACCURACY_DROPPED'
);