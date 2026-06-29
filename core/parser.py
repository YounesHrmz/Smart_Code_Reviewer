import ast

def extract_code_features(file_path):
    """
    يقوم هذا التابع بفتح ملف البايثون المرفوع وتفكيكه برمجياً 
    باستخدام مكتبة AST لاستخراج الدوال والخصائص الهيكلية.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    try:
        # تحويل النص البرمجي بالكامل إلى شجرة AST
        tree = ast.parse(source_code)
    except SyntaxError as e:
        # في حال كان الملف المرفوع يحتوي على أخطاء قواعدية تمنع تشغيله
        return {"error": f"Syntax error in the uploaded file: {e}"}

    extracted_snippets = []

    # المرور على كافة العقد (Nodes) داخل الشجرة البرمجية
    for node in ast.walk(tree):
        
        # 1. استخراج الدوال ككتل برمجية منفصلة (Function Definitions)
        if isinstance(node, ast.FunctionDef):
            # الحصول على نص الدالة بالكامل من الكود الأصلي
            func_lines = source_code.splitlines()[node.lineno - 1 : node.end_lineno]
            func_code = "\n".join(func_lines)
            
            extracted_snippets.append({
                "line_no": node.lineno,
                "type": "function",
                "name": node.name,
                "code": func_code
            })

        # 2. استخراج عمليات ربط النصوص التي قد تشير إلى ثغرات SQL Injection
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            # البحث عن عمليات دمج نصوص في أسطر برمجية منفصلة
            line_no = node.lineno
            line_code = source_code.splitlines()[line_no - 1].strip()
            
            # التأكد من عدم تكرار إضافة نفس السطر
            if not any(s["line_no"] == line_no for s in extracted_snippets):
                extracted_snippets.append({
                    "line_no": line_no,
                    "type": "expression",
                    "name": "string_concatenation",
                    "code": line_code
                })

    return extracted_snippets

if __name__ == "__main__":
    test_code = """
def bad_func(x):
    return x
    
query = "SELECT * FROM users WHERE id = " + user_input
    """
    # إنشاء ملف مؤقت للاختبار
    temp_file = "temp_test.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(test_code)
        
    # تشغيل الفحص
    results = extract_code_features(temp_file)
    print("\n--- AST Parser Test Results ---")
    for r in results:
        print(f"Line {r['line_no']} [{r['type']}]: {r['code']}")
        
    # تنظيف الملف المؤقت
    import os
    os.remove(temp_file)