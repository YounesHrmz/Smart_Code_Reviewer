from app import create_app
from app.services.review_service import CodeReviewService

# إنشاء التطبيق
app = create_app()

# استخدام الخدمة مباشرة
service = CodeReviewService()

# كود اختبار يحتوي على مشاكل مختلفة
test_code = '''
import os
import subprocess

# مشكلة أمنية: كلمة مرور مضمّنة
PASSWORD = "admin123"

# مشكلة أمنية: use of eval
def calculate(expression):
    return eval(expression)

# مشكلة أمنية: os.system
def delete_file(path):
    os.system("rm -rf " + path)

# مشكلة نظافة: اسم متغير سيء
def do_stuff(x, y):
    tmp = x + y
    return tmp

# مشكلة تعقيد: تداخل عميق
def complex_function(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                if a + b > c:
                    return "All positive and sum > c"
                else:
                    return "All positive but sum <= c"
            else:
                return "c is not positive"
        else:
            return "b is not positive"
    else:
        return "a is not positive"

# كود جيد
def safe_read_file(filepath):
    """Read file safely using with statement."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# مشكلة SQL Injection
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return query
'''

# تحليل الكود
result = service.process_file_analysis("test_file.py", test_code)

# عرض النتائج
print("=" * 60)
print("📊 نتائج التحليل")
print("=" * 60)

scores = result['scores']
print(f"🔒 مؤشر الأمان:      {scores['security']}%")
print(f"🧹 مؤشر نظافة الكود: {scores['clean_code']}%")
print(f"📈 مؤشر الجودة:      {scores['quality']}%")
print(f"⭐ المعدل العام:     {scores['overall']}%")
print(f"🎯 متوسط الثقة:      {result['avg_confidence']}")
print(f"📋 إجمالي المشكلات:  {result['summary']['total_issues']}")

print("\n" + "=" * 60)
print("📝 التوصيات:")
print("=" * 60)
for i, rec in enumerate(result['summary']['recommendations'], 1):
    print(f"{i}. {rec}")

print("\n" + "=" * 60)
print("🔍 التفاصيل:")
print("=" * 60)
for item in result['report']:
    if item['status'] != "السطر سليم برمجياً":
        print(f"\n📌 السطر {item['line']} | {item['status']}")
        print(f"   الكود: {item['code'][:60]}...")
        print(f"   المشكلة: {item['problem_description'][:100]}...")