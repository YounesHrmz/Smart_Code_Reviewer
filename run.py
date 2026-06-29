from app import create_app

app = create_app()

if __name__ == '__main__':
    # تشغيل النظام محلياً بالكامل على المنفذ الافتراضي 5000 مع تفعيل وضع التطوير
    app.run(host='127.0.0.1', port=5000, debug=True)