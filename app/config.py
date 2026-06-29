import os

class Config:
    """
    الملف المركزي لإعدادات النظام الأكاديمي.
    يحتوي على كافة المسارات الحيوية للبيئة المحلية والعتبات الرياضية المنظمة للتعلم الذاتي.
    """
    # المسار الجغرافي الأساسي للمشروع
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # مسارات ملفات قاعدة البيانات والنماذج والتقارير
    DB_PATH = os.path.join(BASE_DIR, 'app', 'database', 'analyzer.db')
    MODEL_DIR = os.path.join(BASE_DIR, 'trained_models')
    DATASET_DIR = os.path.join(BASE_DIR, 'datasets')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    
    # إعدادات واجهة Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'principal_architect_secret_key_2026')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    
    # العتبات الرياضية الخاصة بحلقة التعلم المستمر المستقل الذاتي (Autonomous Self-Learning Loop)
    CONFIDENCE_THRESHOLD = 0.90      # $IF confidence >= 0.90$ يتم حقن العينة تلقائياً
    RETRAINING_SAMPLE_LIMIT = 50     # يعاد التدريب تلقائياً بعد جمع 50 عينة فريدة وموثوقة
    
    # التأكد من إنشاء المجلدات الحيوية محلياً عند بدء النظام فوراً
    @classmethod
    def init_folders(cls):
        folders = [cls.MODEL_DIR, cls.DATASET_DIR, cls.LOG_DIR, cls.UPLOAD_FOLDER]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

# تفعيل المجلدات فور استدعاء ملف الإعدادات
Config.init_folders()