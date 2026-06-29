import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from app.config import Config
from app.ml.feature_extractor import HybridFeatureExtractor

class MLRetrainingPipeline:
    """
    محرك تدريب وتقييم النماذج ومقارنتها أكاديمياً عبر الـ Cross-Validation 
    لاختيار وحفظ أفضل نموذج مستقر برمجياً.
    """
    def __init__(self):
        self.model_path = os.path.join(Config.MODEL_DIR, 'best_classifier.joblib')

    def run_pipeline(self, training_data: list) -> dict:
        """
        تستقبل البيانات، تقارن النماذج، وتحدث المودل محلياً إذا ثبتت أفضليته
        """
        if len(training_data) < 5:
            return {'status': 'FAILED', 'message': 'Insufficient data to train.'}

        X_raw = [row['code_snippet'] for row in training_data]
        # دمج الفئة مع النتيجة لتكوين Label مركب مثل (security_bad) لتدريب دقيق
        y = [f"{row['predicted_category']}_{row['predicted_label']}" for row in training_data]

        # استخراج الميزات باستخدام extractor مضبوط على وضع التدريب True
        extractor = HybridFeatureExtractor(is_training=True)
        X = extractor.extract_features(X_raw)

        # تعريف النماذج البرمجية للمقارنة الأكاديمية
        models = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            'SVM': SVC(probability=True, kernel='linear', random_state=42),
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42)
        }

        best_score = -1
        best_model_name = None
        best_model_object = None

        # إجراء الـ Cross-Validation (3-Folds نظراً لحجم البيانات الأولي)
        for name, model in models.items():
            scores = cross_val_score(model, X, y, cv=min(3, len(set(y))), scoring='accuracy')
            mean_score = np.mean(scores)
            
            if mean_score > best_score:
                best_score = mean_score
                best_model_name = name
                best_model_object = model

        # تدريب النموذج الأفضل على كامل البيانات وحفظه
        best_model_object.fit(X, y)
        
        # الاحتفاظ بنسخة احتياطية (Backup) إذا كان هناك نموذج قديم مسبقاً
        if os.path.exists(self.model_path):
            backup_path = os.path.join(Config.MODEL_DIR, 'backup_classifier.joblib')
            os.replace(self.model_path, backup_path)

        joblib.dump(best_model_object, self.model_path)

        return {
            'status': 'SUCCESS_UPGRADED',
            'best_model': best_model_name,
            'accuracy': float(best_score)
        }