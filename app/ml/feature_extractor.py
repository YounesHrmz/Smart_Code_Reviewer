import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from app.config import Config
from app.analyzers.ast_parser import ASTParser


class HybridFeatureExtractor:
    """
    مستخرج الميزات الهجين: يدمج بين الخصائص اللغوية النصية (TF-IDF)
    والمؤشرات الهيكلية الرقمية المستخرجة عبر الـ AST.
    """

    def __init__(self, is_training=False):
        self.is_training = is_training
        self.vectorizer_path = os.path.join(Config.MODEL_DIR, "tfidf_vectorizer.joblib")

        if is_training:
            self.tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", max_features=500)
        else:
            if os.path.exists(self.vectorizer_path):
                self.tfidf = joblib.load(self.vectorizer_path)
            else:
                self.tfidf = TfidfVectorizer(
                    token_pattern=r"(?u)\b\w+\b", max_features=500
                )

    def extract_features(self, code_snippets: list) -> np.ndarray:
        if self.is_training:
            text_features = self.tfidf.fit_transform(code_snippets).toarray()
            joblib.dump(self.tfidf, self.vectorizer_path)
        else:
            try:
                text_features = self.tfidf.transform(code_snippets).toarray()
            except Exception:
                text_features = np.zeros((len(code_snippets), 500))

        structural_list = []
        for code in code_snippets:
            parser = ASTParser(code)
            metrics = parser.extract_structural_metrics()

            if not metrics:
                metrics = {
                    k: 0
                    for k in [
                        "num_functions",
                        "num_classes",
                        "num_imports",
                        "num_loops",
                        "num_conditions",
                        "num_comments",
                        "num_docstrings",
                        "max_nesting_depth",
                        "avg_function_length",
                    ]
                }

            structural_list.append(list(metrics.values()))

        structural_features = np.array(structural_list)
        combined_features = np.hstack((text_features, structural_features))
        return combined_features
