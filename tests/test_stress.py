import sqlite3
import time
import threading
import concurrent.futures
import tempfile
import os
import pytest

# =========================================================
# إعدادات اختبار الجهد
# =========================================================
NUM_USERS = 5000  # عدد الخيوط المتزامنة
TOTAL_TASKS = 10000  # العدد الإجمالي لعمليات الإدراج
RESULTS_LOCK = threading.Lock()  # قفل لتحديث العدادات المشتركة بشكل آمن


# =========================================================
# (A) النسخة المعدلة لـ RealDatabase (آمنة للخيوط)
# =========================================================
class SafeRealDatabase:
    """نسخة آمنة للخيوط من قاعدة البيانات تستخدم ملفاً مؤقتاً على القرص."""

    TEMP_DB_PATH = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False).name
    # FIX 1: زيادة عدد المحاولات لتجاوز أخطاء القفل المتكررة
    MAX_RETRIES = 20
    # FIX 2: زيادة طفيفة في تأخير إعادة المحاولة
    RETRY_DELAY = 0.01
    # FIX 3: زيادة المهلة الكلية لـ SQLite للسماح بمزيد من الانتظار
    CONNECTION_TIMEOUT = 10.0  # المهلة بالثواني

    def __init__(self):
        # تهيئة قاعدة البيانات والتأكد من إنشاء الجدول
        conn = sqlite3.connect(self.TEMP_DB_PATH, check_same_thread=False, timeout=self.CONNECTION_TIMEOUT)
        conn.execute("CREATE TABLE IF NOT EXISTS tasks (name TEXT UNIQUE COLLATE NOCASE, completed INTEGER)")
        conn.commit()
        conn.close()

    def _get_connection(self):
        """يُنشئ اتصالاً جديداً لمجرى التنفيذ الحالي مع المهلة الصحيحة."""
        # تمرير المهلة الصحيحة إلى sqlite3.connect
        return sqlite3.connect(self.TEMP_DB_PATH, check_same_thread=False, timeout=self.CONNECTION_TIMEOUT)

    def insert(self, task):
        # لم يعد هناك حاجة لتعيين conn.timeout هنا لأنه تم تعيينه في _get_connection
        for attempt in range(self.MAX_RETRIES):
            conn = self._get_connection()
            try:
                # 🛑 تمت إزالة السطر conn.timeout = 5 🛑
                conn.execute("INSERT INTO tasks (name, completed) VALUES (?, ?)",
                             (task['name'], int(task['completed'])))
                conn.commit()
                conn.close()
                return True
            except sqlite3.IntegrityError:
                conn.close()
                return False
            except sqlite3.OperationalError as e:
                conn.close()
                if 'database is locked' in str(e) and attempt < self.MAX_RETRIES - 1:
                    # نستخدم تأخير إعادة المحاولة المتزايد (Exponential Backoff)
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    # إذا كان خطأ آخر أو نفدت المحاولات
                    # نطبع الخطأ غير المتوقع ونرفعه
                    print(f"FATAL DB ERROR after {attempt + 1} attempts: {e}")
                    raise e
            except Exception as e:
                conn.close()
                raise e
        return False

    def count_tasks(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        result = cursor.fetchone()[0]
        conn.close()
        return result

    def cleanup(self):
        """إزالة ملف قاعدة البيانات المؤقت."""
        if os.path.exists(self.TEMP_DB_PATH):
            os.remove(self.TEMP_DB_PATH)


class TaskService:
    def __init__(self, db):
        self.db = db

    def create_task(self, name):
        if name is None or not str(name).strip():
            raise ValueError("Task name cannot be empty or just whitespace.")
        task_name = str(name).strip()
        if not self.db.insert({"name": task_name, "completed": False}):
            return False
        return True


# =========================================================
# (C) دالة الاختبار الفعلية (Pytest Test Function)
# =========================================================

def create_task_concurrently(service, task_id, results):
    """العملية التي يتم تشغيلها في كل خيط."""
    task_name = f"Task_{task_id}"

    try:
        success = service.create_task(task_name)

        with RESULTS_LOCK:
            if success:
                results['success'] += 1
            else:
                results['duplicate_error'] += 1

    except Exception as e:
        with RESULTS_LOCK:
            results['unexpected_error'] += 1
            print(f"ERROR: Unexpected exception: {e}")


def test_stress_task_creation():
    """
    اختبار الجهد: محاكاة 500 مستخدم يحاولون إنشاء 1000 مهمة
    للتأكد من سلامة البيانات في ظروف التزامن.
    """
    # NOTE: تم إعادة تعيين TOTAL_TASKS إلى 1000
    global TOTAL_TASKS

    db = SafeRealDatabase()
    service = TaskService(db)

    results = {'success': 0, 'duplicate_error': 0, 'unexpected_error': 0}

    print(f"\n--- بدء اختبار الجهد ({NUM_USERS} مستخدم متزامن) ---")
    start_time = time.time()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
            # نرسل دفعة من المهام للمعالجة
            futures = [executor.submit(create_task_concurrently, service, i, results) for i in range(TOTAL_TASKS)]
            concurrent.futures.wait(futures)

        end_time = time.time()

        total_time = end_time - start_time
        tasks_in_db = db.count_tasks()

        print("\n--- تقرير اختبار الجهد ---")
        print(f"مدة التشغيل الكلية: {total_time:.4f} ثانية")
        print(f"عدد المهام التي تم حفظها: {tasks_in_db}")
        print("--------------------------------")

        # التحقق الأول: هل جميع المهام التي أرسلناها موجودة؟
        assert tasks_in_db == TOTAL_TASKS, (
            f"Data integrity failed: Expected {TOTAL_TASKS} tasks, but found {tasks_in_db}. "
            f"Check for concurrency or locking issues."
        )

        # التحقق الثاني: هل حدثت أي أخطاء غير متوقعة؟
        assert results['unexpected_error'] == 0, (
            f"System stability failed: {results['unexpected_error']} unexpected errors occurred."
        )

        print(f"✅ النجاح: اجتاز النظام اختبار الضغط بنجاح. ({TOTAL_TASKS / total_time:.2f} عملية/ثانية)")

    finally:
        # خطوة التنظيف لضمان إزالة ملف قاعدة البيانات المؤقت
        db.cleanup()
