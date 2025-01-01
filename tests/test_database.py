import unittest
from pathlib import Path
from datetime import datetime, timedelta
import os
from pocut.utils import PomodoroDB, Task, Session


class TestPomodoroDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = Path("test_pomodoro.db")
        cls.pomodoro_db = PomodoroDB(db_path=cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        cls.pomodoro_db.connection.close()
        if cls.test_db_path.exists():
            os.remove(cls.test_db_path)

    def setUp(self):
        self.pomodoro_db.connection.execute("DELETE FROM tasks")
        self.pomodoro_db.connection.execute("DELETE FROM sessions")

    def test_add_and_get_task(self):
        task = Task(
            title="Test Task",
            text="This is a test task.",
            completed=False,
            priority=2,
            category_id=None,
            attempts=0,
            time_spent=0,
            due_date=datetime.now() + timedelta(days=1),
            is_daily=True,
            is_weekly=False,
            is_monthly=False,
            is_yearly=False,
            days_of_week=["Monday"],
        )

        task_id = self.pomodoro_db.add_task(task)
        retrieved_task = self.pomodoro_db.get_task(task_id)

        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.title, task.title)
        self.assertEqual(retrieved_task.completed, task.completed)
        self.assertEqual(retrieved_task.priority, task.priority)

    def test_update_task(self):
        task = Task(title="Initial Task")
        task_id = self.pomodoro_db.add_task(task)

        task_to_update = self.pomodoro_db.get_task(task_id)
        task_to_update.title = "Updated Task"
        task_to_update.completed = True
        self.pomodoro_db.update_task(task_to_update)

        updated_task = self.pomodoro_db.get_task(task_id)
        self.assertEqual(updated_task.title, "Updated Task")
        self.assertTrue(updated_task.completed)

    def test_delete_task(self):
        task = Task(title="Task to Delete")
        task_id = self.pomodoro_db.add_task(task)

        self.pomodoro_db.delete_task(task_id)
        self.assertIsNone(self.pomodoro_db.get_task(task_id))

    def test_list_tasks(self):
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        self.pomodoro_db.add_task(task1)
        self.pomodoro_db.add_task(task2)

        tasks = self.pomodoro_db.list_tasks()
        self.assertEqual(len(tasks), 2)

    def test_add_and_get_session(self):
        session = Session(start_time=datetime.now(), tasks=[], completed=False)

        session_id = self.pomodoro_db.add_session(session)
        retrieved_session = self.pomodoro_db.get_session(session_id)

        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.completed, session.completed)

    def test_update_session(self):
        session = Session(start_time=datetime.now(), tasks=[1, 2])
        session_id = self.pomodoro_db.add_session(session)

        session_to_update = self.pomodoro_db.get_session(session_id)
        session_to_update.completed = True
        session_to_update.end_time = datetime.now()
        self.pomodoro_db.update_session(session_to_update)

        updated_session = self.pomodoro_db.get_session(session_id)
        self.assertTrue(updated_session.completed)
        self.assertIsNotNone(updated_session.end_time)

    def test_delete_session(self):
        session = Session(start_time=datetime.now())
        session_id = self.pomodoro_db.add_session(session)

        self.pomodoro_db.delete_session(session_id)
        self.assertIsNone(self.pomodoro_db.get_session(session_id))

    def test_list_sessions(self):
        session1 = Session(start_time=datetime.now())
        session2 = Session(start_time=datetime.now() + timedelta(hours=1))

        self.pomodoro_db.add_session(session1)
        self.pomodoro_db.add_session(session2)

        sessions = self.pomodoro_db.list_sessions()
        self.assertEqual(len(sessions), 2)

    def test_streak_and_average_calculations(self):
        now = datetime.now()
        session1 = Session(start_time=now, completed=True)
        session2 = Session(start_time=now + timedelta(days=1), completed=True)
        session3 = Session(start_time=now + timedelta(days=2), completed=True)

        self.pomodoro_db.add_session(session1)
        self.pomodoro_db.add_session(session2)
        self.pomodoro_db.add_session(session3)

        stats = self.pomodoro_db.get_streaks_and_averages()

        self.assertEqual(stats["streak"]["daily_streak"], 3)
        self.assertGreaterEqual(stats["average_duration"], 0)


if __name__ == "__main__":
    unittest.main()
