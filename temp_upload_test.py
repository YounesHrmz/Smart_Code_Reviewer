from app import create_app
from app.config import Config
import os
from io import BytesIO
app = create_app()
path = os.path.join(Config.UPLOAD_FOLDER, 'tmp_upload_test.py')
with open(path, 'w', encoding='utf-8') as f:
    f.write('print("hello from upload")\n')
with app.test_client() as client:
    data = {
        'code_file': (open(path, 'rb'), 'tmp_upload_test.py'),
    }
    r = client.post('/review', data=data, content_type='multipart/form-data', follow_redirects=True)
    print('upload file review', r.status_code)
    print(r.data.decode('utf-8', 'replace')[:800])
    r2 = client.get('/export/tmp_upload_test.py/pdf')
    print('export pdf after upload', r2.status_code, r2.content_type)