# tests/test_service.py
import unittest
# استبدلي اسم المستورد إذا أردتِ تشغيل الاختبارات ضد النسخة المعيبة أو المصححة:
# from task_service_with_bug import RealDatabase, TaskService
from ..task_service import RealDatabase, TaskService

class TestTaskServiceIntegration(unittest.TestCase):
    def setUp(self):
        self.db = RealDatabase()
        self.service = TaskService(self.db)

    # def test_create_task_persists_data(self):
    #     task_name = "Finalize Integration Example"
    #     self.service.create_task(task_name)
    #     retrieved = self.db.find(task_name)
    #     self.assertIsNotNone(retrieved, "Task should be persisted to DB")
    #     self.assertEqual(retrieved[0], task_name)
    #     self.assertEqual(retrieved[1], 0)

    def test_create_task_with_invalid_name_raises_error(self):
        # الاختبار يتوقع ValueError عند تمرير اسم فارغ
        with self.assertRaises(ValueError):
            self.service.create_task("")
        self.assertIsNone(self.db.find(""))


if __name__ == "__main__":
    unittest.main()
