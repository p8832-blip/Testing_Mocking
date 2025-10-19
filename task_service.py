# task_service.py
# نسخة مُصلَحة: لا ثغرات — تمنع الأسماء الفارغة، تمنع التكرار (غير حسّاسة للحالة)، وتعالج أخطاء DB.

import sqlite3

class RealDatabase:
    def __init__(self):
        # تعريف الجدول مع UNIQUE و COLLATE NOCASE لمنع التكرار بغض النظر عن حالة الحروف
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (name TEXT UNIQUE COLLATE NOCASE, completed INTEGER)"
        )
        self.conn.commit()

    def insert(self, task):
        # إدخال محمي: نحاول الإدخال ونحوّل IntegrityError إلى ValueError لرسالة أوضح
        try:
            self.cursor.execute(
                "INSERT INTO tasks (name, completed) VALUES (?, ?)",
                (task['name'], int(task['completed']))
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            # يحدث عندما يكون الاسم مكررًا طبقاً لقيد UNIQUE
            raise ValueError(f"Task with name '{task['name']}' already exists.")

    def delete(self, name):
        if name is None:
            return False
        name_to_delete = name.strip()
        if not name_to_delete:
            return False
        self.cursor.execute("DELETE FROM tasks WHERE LOWER(name) = LOWER(?)", (name_to_delete,))
        affected = self.cursor.rowcount
        self.conn.commit()
        return affected > 0

    def find(self, name):
        if name is None:
            return None
        name_to_find = name.strip()
        if not name_to_find:
            return None
        # بحث غير حساس لحالة الحروف لضمان توافق مع CREATE TABLE COLLATE NOCASE
        self.cursor.execute("SELECT name, completed FROM tasks WHERE LOWER(name) = LOWER(?)", (name_to_find,))
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute("SELECT name, completed FROM tasks ORDER BY rowid")
        return [{"name": row[0], "completed": bool(row[1])} for row in self.cursor.fetchall()]


class TaskService:
    def __init__(self, db):
        self.db = db

    def create_task(self, name):
        # التحقق من الاسم الفارغ / المسافات
        if name is None or not str(name).strip():
            raise ValueError("Invalid task name")

        task_name = str(name).strip()

        # فحص احتياطي في طبقة الخدمة قبل الإدخال (يجعل الرسالة أوضح قبل محاولة DB)
        existing = self.db.find(task_name)
        if existing:
            raise ValueError(f"Task with name '{task_name}' already exists.")

        task = {"name": task_name, "completed": False}
        self.db.insert(task)
        return task

    def delete_task(self, name):
        return self.db.delete(name)

    def get_all_tasks(self):
        return self.db.get_all()


def run_cli():
    print("--- Interactive Task Management App (fixed) ---")
    db = RealDatabase()
    service = TaskService(db)
    print("✅ Database and Service initialized successfully.\n")
    print("Available Commands:")
    print("  add <Task Name>   -> add a task")
    print("  del <Task Name>   -> delete a task")
    print("  show              -> show all tasks")
    print("  exit              -> quit\n")

    while True:
        try:
            user_input = input("Enter your command: ").strip()
            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()

            if command == "exit":
                print("Thank you — Goodbye! 👋")
                break

            elif command == "show":
                tasks = service.get_all_tasks()
                print("\n--- Your Task List ---")
                if not tasks:
                    print("Your list is empty.")
                else:
                    for i, task in enumerate(tasks, start=1):
                        status = "✅ Completed" if task["completed"] else "⏳ Pending"
                        print(f"{i}. {task['name']} | {status}")
                print("")

            elif command == "add":
                if len(parts) < 2:
                    print("❌ Error: 'add' requires a task name.")
                    continue
                name = parts[1]
                try:
                    added = service.create_task(name)
                    print(f"🎉 Successfully added task: '{added['name']}'.\n")
                except ValueError as e:
                    print(f"🛑 Input Error: {e}\n")

            elif command == "del":
                if len(parts) < 2:
                    print("❌ Error: 'del' requires a task name.")
                    continue
                name = parts[1]
                deleted = service.delete_task(name)
                if deleted:
                    print(f"🗑️ Successfully deleted task: '{name}'.\n")
                else:
                    print(f"⚠️ Task '{name}' not found or invalid name.\n")

            else:
                print(f"❌ Unknown command: '{command}'.\n")

        except Exception as e:
            # احتياطي: نعرض الاستثناء لكن لا نكسر الحلقة
            print(f"🛑 Unexpected Error: {e}\n")


if __name__ == "__main__":
    run_cli()
