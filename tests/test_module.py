import unittest
from Testing_Mocking.task_module import add_task

class TestAddTask(unittest.TestCase):

    def test_add_valid_task(self):
        tasks = []
        result = add_task("Study", tasks)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(result["name"], "Study")
        self.assertFalse(result["completed"])





    # def test_add_task_with_null_name(self):
    #     tasks = []
    #     with self.assertRaises(ValueError):
    #         add_task("", tasks)

    """
        def test_add_duplicate_task(self):
        tasks = []
        add_task("Study", tasks)
        with self.assertRaises(ValueError):
            add_task("Study", tasks)
    """




if __name__ == "__main__":
    unittest.main()