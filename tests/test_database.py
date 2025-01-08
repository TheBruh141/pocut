"""
test_database.py

    This file contains test cases for the database interface of the Pomodoro application.
    It includes tests to verify the integrity, functionality, and edge cases of operations
    such as adding, updating, deleting tasks, managing sessions, and handling tracked tasks.

    The tests are organized into separate classes based on the functionality they test,
    such as Task operations, Session operations, and Edge cases. Each test aims to ensure
    that the PomodoroDB interacts correctly with task and session data, handles errors
    appropriately, and maintains data consistency.

Fixtures:
    - `temp_db`: Creates a temporary instance of the PomodoroDB for testing, ensuring
      a unique and isolated database file is used for each test.
    - `sample_task`: Provides a default Task object for testing task operations.
    - `sample_session`: Provides a default Session object for testing session operations.

Classes:
    TestTaskOperations:
        - Tests for adding, updating, deleting, and listing tasks in the database.

    TestSessionOperations:
        - Tests for starting and ending sessions, adding sessions to the database,
          and retrieving streaks and averages.

    TestTrackedTaskOperations:
        - Tests for tracking tasks during a session, ending task tracking,
          and handling ongoing tracked tasks.

    TestEdgeCases:
        - Tests to verify edge cases such as database connection errors,
          concurrent updates, and handling invalid data.
"""

import json
import os
import time

from asyncio import sleep
from random import randint

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sqlite3
from typing import Generator

from pocut.utils.task import Task, Session
from pocut.utils.taskmanager import PomodoroDB

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
@pytest.mark.usefixtures("request")
def temp_db(tmp_path) -> Generator[PomodoroDB, None, None]:
    # Create a 'databases' folder inside the /tests directory
    databases_folder = Path("tests") / "databases"
    databases_folder.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename for each test (based on function name)
    db_filename = f"{tmp_path.stem}_{os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]}.db"  # Unique for each test
    db_path = databases_folder / db_filename

    #  Delete the database after the test
    if db_path.exists():
        db_path.unlink()

    # Initialize the database
    db = PomodoroDB(db_path)

    # Yield the database object for the test to use
    yield db


@pytest.fixture
def sample_task() -> Task:
    return Task(
        title="Test Task",
        text="Test Description",
        priority=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        time_spent=0,
    )


@pytest.fixture
def sample_session() -> Session:
    return Session(
        start_time=datetime.now(timezone.utc),
        tasks=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class TestTaskOperations:
    def test_add_task(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)
            assert task_id > 0
            saved_task = temp_db.get_task(task_id)
            assert saved_task.title == sample_task.title
        except Exception as e:
            pytest.fail(f"Failed to add task: {str(e)}")

    def test_update_task(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)
            saved_task = temp_db.get_task(task_id)
            saved_task.title = "Updated Title"
            temp_db.update_task(saved_task)
            updated_task = temp_db.get_task(task_id)
            assert updated_task.title == "Updated Title"
        except Exception as e:
            pytest.fail(f"Failed to update task: {str(e)}")

    def test_update_nonexistent_task(self, temp_db: PomodoroDB, sample_task: Task):
        sample_task.id = 999
        with pytest.raises(ValueError):
            temp_db.update_task(sample_task)

    def test_delete_task(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)
            temp_db.delete_task(task_id)
            assert temp_db.get_task(task_id) is None
        except Exception as e:
            pytest.fail(f"Failed to delete task: {str(e)}")

    def test_list_tasks(self, temp_db: PomodoroDB, sample_task: Task):
        try:

            task_id1 = temp_db.add_task(sample_task)
            task_id2 = temp_db.add_task(sample_task)
            tasks = temp_db.list_tasks()
            assert len(tasks) == 2
            assert [t for t in tasks] == [
                temp_db.get_task(task_id1),
                temp_db.get_task(task_id2),
            ]
            print(tasks)
        except Exception as e:
            pytest.fail(f"Failed to list tasks: {str(e)}")


class TestSessionOperations:
    def test_add_session(self, temp_db: PomodoroDB, sample_session: Session):
        try:
            session_id = temp_db.add_session(sample_session)
            assert session_id > 0
            saved_session = temp_db.get_session(session_id)
            assert saved_session.start_time.timestamp() == pytest.approx(
                sample_session.start_time.timestamp(), abs=1
            )
        except Exception as e:
            pytest.fail(f"Failed to add session: {str(e)}")

    def test_start_session(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)
            temp_db.add_task_to_tracking(task_id)
            session_id = temp_db.start_session()
            tracked_tasks = temp_db.get_ongoing_tracked_tasks()
            assert len(tracked_tasks) == 1
            assert tracked_tasks[0]["session_id"] == session_id
        except Exception as e:
            pytest.fail(f"Failed to start session: {str(e)}")

    @pytest.mark.asyncio
    async def test_end_session(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            for _ in range(3):
                task_id = temp_db.add_task(sample_task)
                temp_db.add_task_to_tracking(task_id)
            session_id = temp_db.start_session()

            # Simulate time progression by manually setting current_time
            wait_time = 2

            await sleep(wait_time)
            updated_tasks = temp_db.end_session(session_id)

            assert len(updated_tasks) == 3
            assert (
                updated_tasks[0].time_spent
                == updated_tasks[1].time_spent
                == pytest.approx(wait_time, abs=1)
            )
        except Exception as e:
            pytest.fail(f"Failed to end session: {str(e)}")

    def test_end_nonexistent_session(self, temp_db: PomodoroDB):
        with pytest.raises(ValueError):
            temp_db.end_session(999)

    def test_get_streaks_and_averages(
        self, temp_db: PomodoroDB, sample_session: Session
    ):
        try:
            # Create sessions on consecutive days
            base_time = datetime.now(timezone.utc)
            for i in range(3):
                session = sample_session
                session.start_time = base_time + timedelta(days=i)
                session.end_time = session.start_time + timedelta(minutes=25)
                session.completed = True
                temp_db.add_session(session)

            stats = temp_db.get_streaks_and_averages()
            assert stats["streak"]["daily_streak"] == 3
            assert stats["average_duration"] == pytest.approx(
                1500, abs=1
            )  # 25 minutes in seconds
        except Exception as e:
            pytest.fail(f"Failed to get streaks and averages: {str(e)}")


class TestTrackedTaskOperations:
    def test_add_task_to_tracking(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)
            temp_db.add_task_to_tracking(task_id)
            tracked_tasks = temp_db.get_ongoing_tracked_tasks()
            assert len(tracked_tasks) == 1
            assert tracked_tasks[0]["task_id"] == task_id
        except Exception as e:
            pytest.fail(f"Failed to add task to tracking: {str(e)}")

    def test_end_task_tracking(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)
            temp_db.add_task_to_tracking(task_id)
            session_id = temp_db.start_session()

            temp_db.end_task_tracking(task_id, session_id)

            tracked_tasks = temp_db.get_ongoing_tracked_tasks()
            assert len(tracked_tasks) == 0
        except Exception as e:
            pytest.fail(f"Failed to end task tracking: {str(e)}")

    def test_end_nonexistent_task_tracking(self, temp_db: PomodoroDB):
        with pytest.raises(ValueError):
            temp_db.end_task_tracking(999, 999)


class TestEdgeCases:
    def test_database_connection_error(self):
        invalid_path = Path("/nonexistent/path/db.sqlite")
        with pytest.raises(sqlite3.OperationalError):
            PomodoroDB(invalid_path)

    def test_concurrent_updates(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)

            # Simulate concurrent updates
            db1 = PomodoroDB(temp_db.db_path)
            db2 = PomodoroDB(temp_db.db_path)

            task1 = db1.get_task(task_id)
            task2 = db2.get_task(task_id)

            task1.title = "Update 1"
            task2.title = "Update 2"

            db1.update_task(task1)
            db2.update_task(task2)

            final_task = temp_db.get_task(task_id)
            assert final_task.title == "Update 2"
        except Exception as e:
            pytest.fail(f"Failed to handle concurrent updates: {str(e)}")

    def test_invalid_json_data(self, temp_db: PomodoroDB, sample_task: Task):
        try:
            task_id = temp_db.add_task(sample_task)
            with temp_db.get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET days_of_week = ? WHERE id = ?",
                    ("invalid json", task_id),
                )

            with pytest.raises(json.JSONDecodeError):
                temp_db.get_task(task_id)
        except Exception as e:
            pytest.fail(f"Failed to handle invalid JSON data: {str(e)}")


class TestLoadPerformance:
    def test_add_many_tasks(self, temp_db: PomodoroDB, sample_task: Task):
        num_tasks = 1000  # Adjust based on the load you want to test

        start_time = time.time()
        for i in range(num_tasks):
            task = Task(
                title=f"Task {i}",
                text=f"Test Description {i}",
                priority=randint(1, 5),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                time_spent=0,
            )
            temp_db.add_task(task)

        end_time = time.time()
        duration = end_time - start_time
        print(f"Adding {num_tasks} tasks took {duration:.2f} seconds.")
        assert duration < 10  # Ensure the task creation completes in under 10 seconds

    def test_add_many_sessions(self, temp_db: PomodoroDB, sample_session: Session):
        num_sessions = 500  # Adjust based on load expectations

        start_time = time.time()
        for i in range(num_sessions):
            session = Session(
                start_time=datetime.now(timezone.utc),
                tasks=[],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            temp_db.add_session(session)

        end_time = time.time()
        duration = end_time - start_time
        print(f"Adding {num_sessions} sessions took {duration:.2f} seconds.")
        assert (
            duration < 10
        )  # Ensure the session creation completes in under 10 seconds

    @pytest.mark.asyncio
    async def test_end_multiple_sessions(self, temp_db: PomodoroDB, sample_task: Task):
        num_sessions = 100  # Simulate a large number of sessions ending

        # Add tasks for sessions to track
        for _ in range(num_sessions):
            task_id = temp_db.add_task(sample_task)
            temp_db.add_task_to_tracking(task_id)

        session_id = temp_db.start_session()

        start_time = time.time()
        await sleep(2)  # Simulate session duration
        updated_tasks = temp_db.end_session(session_id)

        end_time = time.time()
        duration = end_time - start_time
        print(f"Ending {num_sessions} sessions took {duration:.2f} seconds.")
        assert duration < 5  # Ensure all sessions end within 5 seconds

    def test_concurrent_task_operations(self, temp_db: PomodoroDB, sample_task: Task):
        num_tasks = 500  # Number of concurrent tasks to simulate

        def task_operations():
            for i in range(num_tasks):
                task = Task(
                    title=f"Task {i}",
                    text=f"Test Description {i}",
                    priority=randint(1, 5),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    time_spent=0,
                )
                temp_db.add_task(task)
                task_id = temp_db.add_task(task)
                task = temp_db.get_task(task_id)
                task.title = f"Updated Task {i}"
                temp_db.update_task(task)
                temp_db.delete_task(task_id)

        start_time = time.time()

        # Run operations concurrently using threading
        from threading import Thread

        threads = []
        for _ in range(10):  # 10 concurrent threads
            thread = Thread(target=task_operations)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        duration = end_time - start_time
        print(
            f"Performing {num_tasks} concurrent task operations took {duration:.2f} seconds."
        )
        assert duration < 20  # Ensure the operations complete within 20 seconds
