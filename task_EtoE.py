# task_E2E.py
import sqlite3

class RealDatabase:
    """In-memory SQLite DB with case-insensitive UNIQUE on name."""
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        # استخدمنا COLLATE NOCASE لمنع التكرار بغض النظر عن حالة الحروف
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (name TEXT UNIQUE COLLATE NOCASE, completed INTEGER)"
        )
        self.conn.commit()

    def insert(self, task):
        try:
            # صرحنا أسماء الأعمدة صراحة
            self.cursor.execute(
                "INSERT INTO tasks (name, completed) VALUES (?, ?)",
                (task['name'], int(task['completed']))
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all(self):
        # ترتيب ثابت حسب الإدخال
        self.cursor.execute("SELECT name, completed FROM tasks ORDER BY rowid")
        return [{"name": row[0], "completed": bool(row[1])} for row in self.cursor.fetchall()]

    def update_completion(self, name, completed):
        # نستخدم نفس سلوك الـ COLLATE NOCASE في WHERE بواسطة LOWER() أو نعتمد COLLATE NOCASE
        self.cursor.execute("UPDATE tasks SET completed = ? WHERE LOWER(name) = LOWER(?)", (int(completed), name.strip()))
        affected = self.cursor.rowcount
        self.conn.commit()
        return affected > 0

    def find(self, name):
        if name is None:
            return None
        n = name.strip()
        if not n:
            return None
        self.cursor.execute("SELECT name, completed FROM tasks WHERE LOWER(name) = LOWER(?)", (n,))
        return self.cursor.fetchone()


class TaskService:
    def __init__(self, db):
        self.db = db

    def create_task(self, name):
        if name is None or not str(name).strip():
            raise ValueError("Task name cannot be empty or just whitespace.")
        task_name = str(name).strip()
        if not self.db.insert({"name": task_name, "completed": False}):
            raise ValueError(f"Task with name '{task_name}' already exists.")
        return {"name": task_name, "completed": False}

    def get_all_tasks(self):
        return self.db.get_all()

    def mark_task_complete(self, name):
        if name is None or not str(name).strip():
            raise ValueError("Task name cannot be empty or just whitespace.")
        task_name = str(name).strip()
        return self.db.update_completion(task_name, True)


def run_cli_app():
    db = RealDatabase()
    service = TaskService(db)

    print("--- Task Management CLI App ---")
    print("Commands: add <name> | show | mark <name> | exit")

    while True:
        try:
            user_input = input(">> ").strip()
            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()

            if command == 'exit':
                print("Goodbye!")
                break
            elif command == 'show':
                tasks = service.get_all_tasks()
                print("\n--- Current Tasks ---")
                if not tasks:
                    print("No tasks yet.")
                else:
                    for t in tasks:
                        status = "✅" if t['completed'] else "⏳"
                        print(f"{status} {t['name']}")
                print("---------------------\n")

            elif command == 'add':
                if len(parts) < 2:
                    print("Error: 'add' command requires a task name.")
                    continue
                task_name = parts[1].strip()
                try:
                    created = service.create_task(task_name)
                    print(f"Task '{created['name']}' added.")
                except ValueError as e:
                    print(f"Error: {e}")

            elif command == 'mark':
                if len(parts) < 2:
                    print("Error: 'mark' command requires a task name.")
                    continue
                task_name = parts[1].strip()
                try:
                    updated = service.mark_task_complete(task_name)
                    if updated:
                        print(f"Task '{task_name}' marked as complete.")
                    else:
                        # تمييز حالة: هل المهمة موجودة أم لا
                        exists = db.find(task_name) is not None
                        if exists:
                            print(f"Task '{task_name}' was already complete.")
                        else:
                            print(f"Task '{task_name}' not found.")
                except ValueError as e:
                    print(f"Error: {e}")

            else:
                print("Unknown command.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_cli_app()
