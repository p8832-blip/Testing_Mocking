# test_e2e_cli.py

import unittest
import subprocess
import time
import os

# المسار إلى ملف التطبيق التفاعلي
CLI_APP_PATH = "task_EtoE.py"


class TestE2ECLI(unittest.TestCase):

    def setUp(self):
        # بدء التطبيق في عملية فرعية
        self.process = subprocess.Popen(
            ['python', CLI_APP_PATH],
            stdin=subprocess.PIPE,  # يسمح لنا بإرسال مدخلات
            stdout=subprocess.PIPE,  # يسمح لنا بقراءة مخرجات
            stderr=subprocess.PIPE,  # يسمح لنا بقراءة الأخطاء
            text=True,  # يجعل المدخلات والمخرجات كنص (وليس بايت)
            bufsize=1  # لتلقي المخرجات سطر بسطر
        )
        # الانتظار قليلاً حتى يبدأ التطبيق ويطبع رسالة الترحيب
        time.sleep(0.5)
        self.read_output()  # قراءة أي مخرجات بدء التشغيل

    def tearDown(self):
        # إنهاء العملية الفرعية للتطبيق
        self.process.stdin.write("exit\n")
        self.process.stdin.flush()
        self.process.wait(timeout=2)  # انتظار إنهاء العملية
        self.process.terminate()  # التأكد من إنهاء العملية
        self.process.kill() if self.process.poll() is None else None  # قتلها إذا كانت لا تزال قيد التشغيل

    def send_command(self, command):
        """يرسل أمراً إلى التطبيق ويفرغ البفر."""
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
        time.sleep(0.1)  # انتظار استجابة التطبيق

    def read_output(self):
        """يقرأ جميع المخرجات المتوفرة من التطبيق."""
        output_lines = []
        while True:
            # قراءة سطر واحد مع مهلة قصيرة
            try:
                line = self.process.stdout.readline().strip()
                if line:
                    output_lines.append(line)
                else:
                    break  # لا يوجد المزيد من المخرجات حاليا
            except Exception:
                break
        return "\n".join(output_lines)

    # =========================================================
    # اختبارات E2E الفعلية
    # =========================================================

    def test_e2e_add_and_show_task(self):
        """
        اختبار E2E: إضافة مهمة ثم عرضها.
        يركز على رحلة المستخدم الكاملة من UI إلى DB والعودة إلى UI.
        """
        task_name = "Buy groceries"

        # 1. الإجراء: إضافة المهمة
        self.send_command(f"add {task_name}")
        output = self.read_output()
        self.assertIn(f"Task '{task_name}' added.", output)

        # 2. الإجراء: عرض المهام
        self.send_command("show")
        output = self.read_output()

        # 3. التحقق (E2E Check): التأكد من ظهور المهمة في القائمة المعروضة
        self.assertIn(f"⏳ {task_name}", output)
        self.assertIn("--- Current Tasks ---", output)

    def test_e2e_mark_task_complete(self):
        """
        اختبار E2E: إضافة مهمة، ثم وضع علامة "مكتملة"، ثم عرضها للتحقق.
        """
        task_name = "Finish E2E demo"

        # إضافة المهمة أولاً
        self.send_command(f"add {task_name}")
        self.read_output()  # قراءة مخرج الإضافة

        # وضع علامة "مكتملة"
        self.send_command(f"mark {task_name}")
        output = self.read_output()
        self.assertIn(f"Task '{task_name}' marked as complete.", output)

        # عرض المهام للتحقق من الحالة
        self.send_command("show")
        output = self.read_output()
        self.assertIn(f"✅ {task_name}", output)  # يجب أن تظهر كـ "مكتملة"

    # سؤالك: ما هو السيناريو التالي لـ E2E بعد إضافة مهمة؟ (مثال: وضع علامة مكتملة)
    # الإجابة: test_e2e_mark_task_complete هو مثال على ذلك.


if __name__ == "__main__":
    # تأكد من وجود ملف التطبيق
    if not os.path.exists(CLI_APP_PATH):
        print(f"Error: CLI app '{CLI_APP_PATH}' not found. Please ensure it's in the same directory.")
        exit(1)
    unittest.main()