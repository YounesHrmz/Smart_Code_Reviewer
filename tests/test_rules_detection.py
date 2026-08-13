import unittest

from app.services.review_service import CodeReviewService


class RuleDetectionTests(unittest.TestCase):
    def setUp(self):
        self.service = CodeReviewService()

    def test_detects_subprocess_shell_and_hardcoded_secret_and_sql_concat(self):
        code = """
import subprocess
password = 'secret123'

cmd = "ls -la " + user_input
subprocess.call(cmd, shell=True)
"""
        result = self.service.process_file_analysis("sample_rules.py", code)
        # must detect issues and recommendations
        self.assertGreaterEqual(result["summary"]["total_issues"], 2)
        recs = " ".join(result["summary"]["recommendations"]).lower()
        self.assertTrue(("subprocess" in recs) or ("shell" in recs))
        self.assertTrue(("سر" in recs) or ("secret" in recs))


if __name__ == "__main__":
    unittest.main()
