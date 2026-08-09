import os
from app import create_app
from app.config import Config

app = create_app()
client = app.test_client()

print("POST /review")
resp = client.post(
    "/review", data={"code_text": "print(123)\n", "analysis_mode": "text"}
)
print("review status", resp.status_code)
print("review data", resp.data.decode("utf-8", errors="replace")[:2000])
print("---")

path = os.path.join(Config.UPLOAD_FOLDER, "test.py")
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as f:
    f.write("print(123)\n")

resp = client.get("/export/test.py/pdf")
print("export status", resp.status_code)
print("content-type", resp.headers.get("Content-Type"))
print("export data len", len(resp.data) if resp.status_code == 200 else "err")
