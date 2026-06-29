from app.repositories.base_repository import BaseRepository
from app.database.connection import DBConnection

class AuditRepository(BaseRepository):
    
    def save_log(self, filename, security, clean_code, quality, overall, confidence):
        """
        حفظ تقرير الفحص والنتائج المئوية فور انتهاء التحليل
        """
        query = '''
            INSERT INTO audit_logs (filename, security_score, clean_code_score, quality_score, overall_score, confidence_average)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        with DBConnection() as cursor:
            cursor.execute(query, (filename, security, clean_code, quality, overall, confidence))
            return cursor.lastrowid

    def get_all_logs(self):
        """
        جلب التاريخ الكامل للفحوصات لعرضه في لوحة التحكم التفاعلية
        """
        query = "SELECT * FROM audit_logs ORDER BY upload_time DESC"
        with DBConnection() as cursor:
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]