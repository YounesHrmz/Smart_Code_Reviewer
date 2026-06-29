from app.repositories.base_repository import BaseRepository
from app.database.connection import DBConnection

class SampleRepository(BaseRepository):

    def insert_high_confidence_sample(self, code, category, label, confidence):
        """
        حقن العينات البرمجية المكتشفة تلقائياً التي تخطت عتبة الثقة (CONFIDENCE_THRESHOLD)
        مع الحماية الصارمة من تكرار نفس العينات لمنع Data Poisoning
        """
        check_query = "SELECT id FROM training_samples WHERE code_snippet = ?"
        insert_query = '''
            INSERT INTO training_samples (code_snippet, predicted_category, predicted_label, confidence_score)
            VALUES (?, ?, ?, ?)
        '''
        with DBConnection() as cursor:
            cursor.execute(check_query, (code,))
            if cursor.fetchone():
                return False # العينة موجودة مسبقاً، تم إهمالها لمنع التكرار
            
            cursor.execute(insert_query, (code, category, label, confidence))
            return True

    def get_total_sample_count(self):
        """
        حساب عدد العينات المجمعة حالياً لمراقبة عتبة إعادة التدريب (50 عينة)
        """
        query = "SELECT COUNT(*) as total FROM training_samples"
        with DBConnection() as cursor:
            cursor.execute(query)
            return cursor.fetchone()['total']

    def fetch_all_training_data(self):
        """
        سحب الداتا سيت بالكامل على هيئة أسطر برمجية وتصنيفاتها لتمريرها لمحرك التعلم الآلي
        """
        query = "SELECT code_snippet, predicted_category, predicted_label FROM training_samples"
        with DBConnection() as cursor:
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def log_retraining(self, prev_acc, new_acc, count, status):
        """
        توثيق عمليات إعادة التدريب الذاتي المستمر ونتائجها الإحصائية
        """
        query = '''
            INSERT INTO retraining_logs (previous_accuracy, new_accuracy, samples_count, status)
            VALUES (?, ?, ?, ?)
        '''
        with DBConnection() as cursor:
            cursor.execute(query, (prev_acc, new_acc, count, status))