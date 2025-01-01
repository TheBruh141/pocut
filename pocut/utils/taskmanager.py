import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
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

    def _create_tables(self):
        """
        Creates the `tasks` and `sessions` tables in the database if they don't exist.
        Ensures the structure of the database is set up correctly.
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
                tasks TEXT NOT NULL, -- JSON list of task IDs
                completed BOOLEAN NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
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
        """
        Updates an existing task in the database.

        Args:
            - task: The Task object with updated details (must include a valid ID).
        """
        with self.connection as conn:
            conn.execute(
                """
            UPDATE tasks
            SET title = ?, text = ?, completed = ?, priority = ?, 
                category_id = ?, attempts = ?, time_spent = ?, 
                due_date = ?, is_daily = ?, is_weekly = ?, is_monthly = ?, 
                is_yearly = ?, days_of_week = ?, updated_at = ?
            WHERE id = ?
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
                    task.updated_at.isoformat(),
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

    def _row_to_task(self, row) -> Task:
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
                tasks=json.loads(row["tasks"]),
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
                    tasks=json.loads(row["tasks"]),
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
