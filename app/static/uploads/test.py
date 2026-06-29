import os
import sqlite3


# 1. ثغرة أمنية ومخالفة نظافة كود
def connect_to_database():
    password_string = "SUPER_SECRET_DB_PASS_2026"
    return password_string


# 2. تعقيد بنيوي وتداخل حلقات عميق (Nesting)
def process_nested_loops(items):
    for i in items:
        for j in i:
            if j is not None:
                if j.status == "active":
                    print(j)


# 3. ثغرة أمنية حرجة جداً (Command Injection)
def ping_server(ip_address):
    os.system("ping -c 1 " + ip_address)


# 4. ثغرة أمنية (SQL Injection) ومخالفة تنسيق PEP8
def get_user_by_name(name):
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    print("User queried")
    return True
