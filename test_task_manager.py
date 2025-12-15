import unittest
import os
import json
from unittest.mock import patch, MagicMock, mock_open

from task_manager import Task, TaskManager, Priority

class TestTask(unittest.TestCase):
    def test_task_creation(self):
        task = Task(1, "Testovací úkol")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.name, "Testovací úkol")
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)
        self.assertEqual(task.priority, Priority.MEDIUM)

    def test_mark_completed(self):
        task = Task(1, "Dokončit testy")
        task.mark_completed()
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)

    def test_to_from_dict(self):
        task = Task(1, "Serializace")
        task.priority = Priority.HIGH
        task_dict = task.to_dict()

        self.assertEqual(task_dict['priority'], 'vysoká')

        new_task = Task.from_dict(task_dict)
        self.assertEqual(new_task.id, task.id)
        self.assertEqual(new_task.name, task.name)
        self.assertEqual(new_task.priority, task.priority)


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        patcher_thread = patch('threading.Thread')
        self.addCleanup(patcher_thread.stop)
        patcher_thread.start()

        patcher_open = patch('builtins.open', mock_open())
        self.addCleanup(patcher_open.stop)
        patcher_open.start()

        self.manager = TaskManager()
        self.manager.tasks = []
        self.manager.next_id = 1

    def test_add_task(self):
        self.assertEqual(len(self.manager.tasks), 0)
        task = self.manager.add_task("Nový úkol", "vysoká")
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(task.name, "Nový úkol")
        self.assertEqual(task.id, 1)
        self.assertEqual(self.manager.next_id, 2)
        self.assertEqual(task.priority, Priority.HIGH)

    def test_get_task(self):
        self.manager.add_task("Hledaný úkol")
        found_task = self.manager.get_task(1)
        self.assertIsNotNone(found_task)
        self.assertEqual(found_task.id, 1)

        not_found_task = self.manager.get_task(99)
        self.assertIsNone(not_found_task)

    def test_complete_task(self):
        self.manager.add_task("Dokončit tento úkol")
        result = self.manager.complete_task(1)
        self.assertTrue(result)
        task = self.manager.get_task(1)
        self.assertTrue(task.completed)

        result_fail = self.manager.complete_task(99)
        self.assertFalse(result_fail)

    def test_delete_task(self):
        self.manager.add_task("Smazat tento úkol")
        self.assertEqual(len(self.manager.tasks), 1)
        result = self.manager.delete_task(1)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.tasks), 0)

        result_fail = self.manager.delete_task(99)
        self.assertFalse(result_fail)

    def test_get_stats(self):
        self.manager.add_task("Úkol 1", "vysoká")
        self.manager.add_task("Úkol 2", "střední")
        self.manager.add_task("Úkol 3", "nízká")
        self.manager.complete_task(1)

        stats = self.manager.get_stats()

        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['pending'], 2)
        self.assertEqual(stats['priorities']['vysoká'], 1)
        self.assertEqual(stats['priorities']['střední'], 1)
        self.assertEqual(stats['priorities']['nízká'], 1)


if __name__ == '__main__':
    unittest.main()