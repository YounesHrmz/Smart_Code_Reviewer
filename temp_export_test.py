from app import create_app
from app.config import Config
import os
app = create_app()
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
path = os.path.join(Config.UPLOAD_FOLDER, 'tmp_export_test.py')
with open(path, 'w', encoding='utf-8') as f:
    f.write('print("hello")\n')
with app.test_client() as client:
    for fmt in ['json','html','pdf']:
        r = client.get(f'/export/tmp_export_test.py/{fmt}')
        print(fmt, r.status_code, r.content_type)
        if r.status_code != 200:
            print(r.get_data(as_text=True, errors='replace'))