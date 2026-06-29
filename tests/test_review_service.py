import unittest

from app import create_app
from app.services.review_service import CodeReviewService


class ReviewServiceTests(unittest.TestCase):
    def test_returns_summary_and_recommendations(self):
        service = CodeReviewService()
        code = """
import subprocess

password = 'secret'

def run(cmd):
    return subprocess.call(cmd, shell=True)
"""
        result = service.process_file_analysis("sample.py", code)

        self.assertIn("summary", result)
        self.assertGreaterEqual(result["summary"]["total_issues"], 1)
        self.assertGreaterEqual(len(result["summary"]["recommendations"]), 1)
        self.assertGreaterEqual(len(result["report"]), 1)

    def test_app_routes_render_dashboard_for_text_input(self):
        app = create_app()
        test_client = app.test_client()
        response = test_client.post(
            "/review",
            data={
                "code_text": "import subprocess\nsubprocess.call('ls', shell=True)\n",
                "analysis_mode": "text",
            },
        )
        self.assertIn(response.status_code, (200, 302))


if __name__ == "__main__":
    unittest.main()
