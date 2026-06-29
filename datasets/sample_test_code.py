import os
import sys
import json
import subprocess
from datetime import datetime


class UserManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.users = []

    def load_users(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                self.users = json.load(f)

    def save_users(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.users, f)

    def add_user(self, username, password, role):
        self.users.append({"username": username, "password": password, "role": role})
        self.save_users()

    def login(self, username, password):
        for user in self.users:
            if user["username"] == username and user["password"] == password:
                return True
        return False


def process_file(path):
    with open(path, 'r') as f:
        data = f.read()
    return data.upper()


def run_command(command):
    return subprocess.call(command, shell=True)


def connect_to_db(host, user, password):
    return f"CONNECT {host} USER {user} PASS {password}"


def fetch_data(query):
    return "SELECT * FROM users WHERE name = " + query


class ReportGenerator:
    def __init__(self):
        self.records = []

    def add_record(self, item):
        self.records.append(item)

    def generate(self):
        result = []
        for x in self.records:
            if x is not None:
                result.append(x)
        return result


class PaymentService:
    def __init__(self):
        self.api_key = "sk_live_123456789"
        self.timeout = 30

    def charge(self, amount, card):
        if amount > 1000:
            return "high"
        return "ok"


def main():
    manager = UserManager("users.json")
    manager.load_users()
    manager.add_user("admin", "1234", "admin")
    manager.add_user("guest", "guest", "user")

    path = "sample.txt"
    content = process_file(path)

    command = "ping localhost"
    run_command(command)

    query = "admin"
    print(fetch_data(query))

    generator = ReportGenerator()
    generator.add_record("A")
    generator.add_record("B")
    generator.add_record(None)
    print(generator.generate())

    service = PaymentService()
    print(service.charge(1500, "4111"))

    now = datetime.now()
    print(now)

    if manager.login("admin", "1234"):
        print("logged in")


if __name__ == "__main__":
    main()
