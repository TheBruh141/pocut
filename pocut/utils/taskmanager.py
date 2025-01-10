import json
import sqlite3
from datetime import datetime, timezone
from datetime import timedelta
from pathlib import Path
from sqlite3 import DatabaseError
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

import textual

import pocut.utils.task as task

Task = task.Task
Session = task.Session


class PomodoroDB:
    """
    Manages the database for tasks and Pomodoro sessions.
    Handles CRUD operations for both tasks and sessions, ensuring data persistence.
    """

    def __init__(self, db_path: Path = Path("pomodoro.db")):
        """
        Initializes the database connection and creates necessary tables.

        Args:
            - db_path: Path to the SQLite database file (default: "pomodoro.db").
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enables row access by column name
        self._create_tables()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """
        Creates the `tasks`, `sessions`, and `tracked_tasks` tables in the database if they don't exist.
        """
        with self.connection as conn:
            # Task table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    text TEXT,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    ongoing BOOLEAN NOT NULL DEFAULT 0,
                    priority INTEGER NOT NULL DEFAULT 1,
                    category_id INTEGER,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    time_spent INTEGER NOT NULL DEFAULT 0,
                    due_date TEXT,
                    is_daily BOOLEAN NOT NULL DEFAULT 0,
                    is_weekly BOOLEAN NOT NULL DEFAULT 0,
                    is_monthly BOOLEAN NOT NULL DEFAULT 0,
                    is_yearly BOOLEAN NOT NULL DEFAULT 0,
                    days_of_week TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            # Session table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    tasks TEXT, -- JSON list of task IDs
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            # Tracked Tasks table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tracked_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                session_id INTEGER, -- NULL if the task hasn't been linked to a session yet
                start_time TEXT NOT NULL,
                end_time TEXT, -- NULL if tracking is ongoing
                time_spent INTEGER NOT NULL DEFAULT 0, -- Total time spent on the task
                progress TEXT, -- Optional metadata (e.g., JSON to store task progress)
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            );
                """
            )

    # --- Task CRUD Operations ---

    def add_task(self, task: Task) -> int:
        """
        Adds a new task to the database.

        Args:
            - task: The Task object to add.

        Returns:
            - The ID of the newly created task.
        """
        with self.connection as conn:
            cursor = conn.execute(
                """
            INSERT INTO tasks (
                title, text, completed, priority, category_id, attempts, 
                time_spent, due_date, is_daily, is_weekly, is_monthly, 
                is_yearly, days_of_week, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.title,
                    task.text,
                    task.completed,
                    task.priority,
                    task.category_id,
                    task.attempts,
                    task.time_spent,
                    task.due_date.isoformat() if task.due_date else None,
                    task.is_daily,
                    task.is_weekly,
                    task.is_monthly,
                    task.is_yearly,
                    json.dumps(task.days_of_week),
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )
            return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieves a task by its ID.

        Args:
            - task_id: The ID of the task to retrieve.

        Returns:
            - A Task object if found, otherwise None.
        """
        with self.connection as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            return self._row_to_task(row) if row else None

    def update_task(self, task: Task) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task.id,))
            if not cursor.fetchone():
                raise ValueError(f"Task {task.id} not found")

            conn.execute(
                """
            UPDATE tasks
            SET title = ?, text = ?, completed = ?, ongoing = ?, priority = ?, 
                category_id = ?, attempts = ?, time_spent = ?, 
                due_date = ?, is_daily = ?, is_weekly = ?, is_monthly = ?, 
                is_yearly = ?, days_of_week = ?, updated_at = ?
            WHERE id = ?""",
                (
                    task.title,
                    task.text,
                    task.completed,
                    task.ongoing,
                    task.priority,
                    task.category_id,
                    task.attempts,
                    task.time_spent,
                    task.due_date.isoformat() if task.due_date else None,
                    task.is_daily,
                    task.is_weekly,
                    task.is_monthly,
                    task.is_yearly,
                    json.dumps(task.days_of_week),
                    datetime.now(timezone.utc).isoformat(),
                    task.id,
                ),
            )

    def delete_task(self, task_id: int) -> None:
        """
        Deletes a task from the database.

        Args:
            - task_id: The ID of the task to delete.
        """
        with self.connection as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def list_tasks(self) -> List[Task]:
        """
        Retrieves all tasks from the database.

        Returns:
            - A list of Task objects.
        """
        with self.connection as conn:
            rows = conn.execute("SELECT * FROM tasks").fetchall()
            return [self._row_to_task(row) for row in rows]

    @staticmethod
    def _row_to_task(row) -> Task:
        """
        Converts a database row to a Task object.

        Args:
            - row: A database row representing a task.

        Returns:
            - A Task object.
        """
        return Task(
            id=row["id"],
            title=row["title"],
            text=row["text"],
            completed=bool(row["completed"]),
            ongoing=bool(row["ongoing"]),
            priority=row["priority"],
            category_id=row["category_id"],
            attempts=row["attempts"],
            time_spent=row["time_spent"],
            due_date=(
                datetime.fromisoformat(row["due_date"]) if row["due_date"] else None
            ),
            is_daily=bool(row["is_daily"]),
            is_weekly=bool(row["is_weekly"]),
            is_monthly=bool(row["is_monthly"]),
            is_yearly=bool(row["is_yearly"]),
            days_of_week=json.loads(row["days_of_week"]) if row["days_of_week"] else [],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    # --- Session CRUD Operations ---
    def add_session(self, session: Session) -> int:
        """
        Adds a new session to the database.

        Args:
            - session: The Session object to add.

        Returns:
            - The ID of the newly created session.
        """
        with self.connection as conn:
            cursor = conn.execute(
                """
            INSERT INTO sessions (
                start_time, end_time, tasks, completed, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    session.start_time.isoformat(),
                    session.end_time.isoformat() if session.end_time else None,
                    json.dumps(session.tasks),
                    session.completed,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                ),
            )
            return (
                cursor.lastrowid
            )  # Correct attribute for the ID of the last inserted row

    def get_session(self, session_id: int) -> Optional[Session]:
        with self.connection as conn:

            tasks = conn.execute(
                "SELECT * FROM tracked_tasks where session_id = ?", (session_id,)
            ).fetchall()
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row is None:
                return None  # Return None instead of raising an exception
            return Session(
                id=row["id"],
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=(
                    datetime.fromisoformat(row["end_time"]) if row["end_time"] else None
                ),
                tasks=tasks,
                completed=row["completed"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

    def delete_session(self, session_id: int) -> None:
        with self.connection as conn:
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

    def list_sessions(self) -> List[Session]:
        with self.connection as conn:
            cursor = conn.execute("SELECT * FROM sessions")
            return [
                Session(
                    id=row["id"],
                    start_time=datetime.fromisoformat(row["start_time"]),
                    end_time=(
                        datetime.fromisoformat(row["end_time"])
                        if row["end_time"]
                        else None
                    ),
                    tasks=json.loads(row["tasks"]) if row["tasks"] != "" else [],
                    completed=row["completed"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
                for row in cursor.fetchall()
            ]

    def get_streaks_and_averages(self) -> Dict[str, Any]:
        with self.connection as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE completed = 1 ORDER BY start_time"
            )
            sessions = cursor.fetchall()
            if not sessions:
                return {"streak": {"daily_streak": 0}, "average_duration": 0}

            streak = 1
            max_streak = 1
            for i in range(1, len(sessions)):
                prev_session = datetime.fromisoformat(sessions[i - 1]["start_time"])
                current_session = datetime.fromisoformat(sessions[i]["start_time"])
                if (current_session - prev_session).days == 1:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 1

            total_duration = sum(
                (
                    datetime.fromisoformat(s["end_time"])
                    - datetime.fromisoformat(s["start_time"])
                ).total_seconds()
                for s in sessions
                if s["end_time"]
            )
            average_duration = total_duration / len(sessions)

            return {
                "streak": {"daily_streak": max_streak},
                "average_duration": average_duration,
            }

    def update_session(self, session: Session) -> None:
        updates = {
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "completed": session.completed,
            "tasks": json.dumps(session.tasks),
        }
        fields = ", ".join(f"{key} = ?" for key in updates.keys())
        values = list(updates.values())
        with self.connection as conn:
            conn.execute(
                f"UPDATE sessions SET {fields}, updated_at = ? WHERE id = ?",
                (*values, datetime.now().isoformat(), session.id),
            )

    # --- Tracked Task Handling ---
    def add_task_to_tracking(self, task_id: int) -> None:
        with self.get_connection() as conn:
            now = datetime.now(timezone.utc)
            conn.execute(
                """INSERT INTO tracked_tasks (
                    task_id, start_time, created_at, updated_at
                ) VALUES (?, ?, ?, ?)""",
                (task_id, now.isoformat(), now.isoformat(), now.isoformat()),
            )

    def remove_tracking_tasks(self, task_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute(f"""DELETE FROM tracked_tasks WHERE task_id = {task_id}""")

    def start_session(self) -> int:
        """
        Starts a new session and links all queued tracked tasks to the session.

        Returns:
            - The ID of the newly created session.
        """
        with self.connection as conn:
            # Create a new session
            cursor = conn.execute(
                """
                INSERT INTO sessions (
                    start_time, created_at, updated_at
                ) VALUES (?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            session_id = cursor.lastrowid
            sess = self.get_session(session_id)
            # Assign all unlinked tracked tasks to the new session
            sess.tasks = [task["id"] for task in self.get_ongoing_tracked_tasks()]
            self.update_session(sess)
            cursor.execute(
                """
            UPDATE tracked_tasks 
            SET session_id = ?
            """,
                (session_id,),
            )

            return session_id

    def end_task_tracking(self, task_id: int, session_id: int) -> None:
        with self.get_connection() as conn:
            current_time = datetime.now(timezone.utc)
            task = conn.execute(
                """SELECT start_time FROM tracked_tasks
                   WHERE task_id = ? AND session_id = ? AND end_time IS NULL""",
                (task_id, session_id),
            ).fetchone()

            if task is None:
                raise ValueError("Task is not being tracked in the specified session.")

            start_time = datetime.fromisoformat(task["start_time"])
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)

            time_spent = int(
                (current_time - start_time).total_seconds() / 60
            )  # Time in minutes

            conn.execute(
                """UPDATE tracked_tasks
                   SET end_time = ?, time_spent = ?, updated_at = ?
                   WHERE task_id = ? AND session_id = ?""",
                (
                    current_time.isoformat(),
                    time_spent,
                    current_time.isoformat(),
                    task_id,
                    session_id,
                ),
            )

    def get_ongoing_tracked_tasks(self) -> list[dict]:
        """
        Retrieves all tasks currently being tracked but not yet ended.

        Returns:
            - A list of dictionaries representing ongoing tracked tasks.
        """
        with self.connection as conn:
            rows = conn.execute(
                """
                SELECT * FROM tracked_tasks
                WHERE end_time IS NULL
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def end_session(self, session_id: int) -> list[Task]:
        """
        This function ends an active session, updates the session's end time, and updates the time tracking
        for each tracked task associated with the session.

        Args:
            session_id (int): The ID of the session that needs to be ended.

        Returns:
            list[Task]: A list of Task objects that have been updated with the new time tracking data.

        Raises:
            ValueError: If the session does not exist or has already ended, or if there is an issue with time tracking.
        """
        # Begin a new transaction to ensure that all database changes are atomic
        with self.get_connection() as conn:
            try:
                # Start the transaction
                conn.execute("BEGIN TRANSACTION")

                # Get the current UTC time as the session end time
                current_time = datetime.now(timezone.utc)

                # Check if the session exists and if it hasn't ended yet
                cursor = conn.execute(
                    "SELECT id FROM sessions WHERE id = ? AND end_time IS NULL",
                    (
                        session_id,
                    ),  # The session ID is passed as a parameter to prevent SQL injection
                )

                # If no session is found, or it's already ended, rollback and raise an error
                if not cursor.fetchone():
                    conn.execute("ROLLBACK")
                    raise ValueError("Invalid session or already ended")

                # Update the session's end time and mark it as updated
                conn.execute(
                    "UPDATE sessions SET end_time = ?, updated_at = ?, completed= ? WHERE id = ?",
                    (
                        current_time.isoformat(),
                        current_time.isoformat(),
                        True,
                        session_id,
                    ),
                    # Use ISO 8601 format for datetime
                )

                # Retrieve all tasks that are being tracked in the session
                tracked_tasks = conn.execute(
                    "SELECT * FROM tracked_tasks WHERE session_id = ?",
                    (session_id,),  # The session ID to filter the tracked tasks
                ).fetchall()

                updated_tasks = []  # List to store the updated tasks

                # Iterate through each tracked task to calculate and update time tracking
                for tracked in tracked_tasks:
                    print(tracked)
                    # Convert the start time of the tracked task to a timezone-aware datetime (UTC)
                    start_time = datetime.fromisoformat(tracked["start_time"])
                    if start_time.tzinfo is None:
                        start_time = start_time.replace(
                            tzinfo=timezone.utc
                        )  # Ensure it's UTC-aware

                    # Calculate the time spent on the task by subtracting start time from current time
                    time_spent = int((current_time - start_time).total_seconds())

                    # Debugging: Print the time calculation for the tracked task
                    print(
                        f"Start Time: {start_time}, Current Time: {current_time}, Time Spent: {time_spent}"
                    )

                    # If the calculated time is negative (start_time > current_time), rollback the transaction
                    if time_spent < 0:
                        conn.execute("ROLLBACK")
                        raise ValueError(
                            f"Invalid time calculation for task {tracked['task_id']}"
                        )

                    t = self.get_task(tracked["task_id"])
                    # t.modify(
                    #     updates={
                    #         "time_spent": time_spent + tracked.time_spent,
                    #         "updated_at": datetime.now(timezone.utc),
                    #         "end_time": datetime.now(timezone.utc),
                    #     }
                    # )
                    t.time_spent += time_spent
                    t.updated_at = datetime.now(timezone.utc)

                    conn.execute("COMMIT")
                    #  to not fuck up the timings

                    self.update_task(t)  # this lil fucker locks up the db too

                    conn.execute("BEGIN TRANSACTION")

                    # Update the tracked task with the end time and the calculated time spent
                    conn.execute(
                        """UPDATE tracked_tasks 
                           SET end_time = ?, time_spent = ?, updated_at = ?
                           WHERE task_id = ? AND session_id = ?""",
                        (
                            current_time.isoformat(),  # Set end time to current UTC time
                            time_spent,  # The calculated time spent on the task in seconds
                            current_time.isoformat(),  # Updated timestamp
                            tracked["task_id"],  # The ID of the task being updated
                            session_id,  # The session ID to ensure we update the correct task
                        ),
                    )

                    # # Update the main task table by adding the time spent to the existing value
                    # conn.execute(
                    #     """UPDATE tasks
                    #        SET time_spent = time_spent + ?, updated_at = ?
                    #        WHERE id = ?""",
                    #     (time_spent, current_time.isoformat(), tracked["task_id"]),
                    # )
                    print(
                        f"""
                        {tracked["task_id"]=},
                        {self.get_task(tracked["task_id"]).time_spent=},
                        {tracked["time_spent"]=},
                        """
                    )
                    # Fetch the updated task object and add it to the list
                    updated_tasks.append(self.get_task(tracked["task_id"]))

                # Commit the transaction to persist all changes
                conn.execute("COMMIT")

                # Return the list of updated tasks
                return updated_tasks

            except Exception as e:
                # In case of any error, rollback the transaction to avoid partial updates
                try:
                    conn.execute("ROLLBACK")
                except Exception as e_2:
                    # If rollback fails, raise the original exception
                    raise e_2 and e
                # Raise the exception that caused the failure
                raise e


# Handle task creation
def handle_data_create_headless(data: task.Task) -> None:
    """
    Handles the creation of a new task by inserting it into the database.

    Args:
        data (t.TaskData): Event data containing the task to create.
    """
    db = PomodoroDB()

    try:
        task_id = db.add_task(data)
        print(f"Task created with ID: {task_id}")
    except Exception as e:
        print(f"Error creating task: {e}")


# Handle task updates
def handle_data_update_headless(data: task.Task) -> None:
    """
    Handles updating an existing task in the database.

    Args:
        data (t.TaskData): Event data containing the task to update.
    """
    db = PomodoroDB()

    try:
        data.updated_at = datetime.now()
        db.update_task(data)
        # print(f"Task with ID {data.task.id} updated.")
        textual.log(f"Task updated with ID: {data.id}")
    except Exception as e:
        textual.log(f"Error updating task: {e}", error=True)


# Handle task deletion
def handle_data_delete_headless(data: task.Task) -> None:
    """
    Handles deleting a task from the database.

    Args:
        data (t.TaskData): Event data containing the task to delete.
    """
    db = PomodoroDB()
    try:
        db.delete_task(data.id)
        textual.log(f"Task with ID {data.id} deleted.")
    except Exception as e:
        textual.log(f"Error deleting task: {e}", error=True)
