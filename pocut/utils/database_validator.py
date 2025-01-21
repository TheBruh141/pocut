"""
not used as of now

"""

import threading
from contextlib import contextmanager
from typing import List, Dict, Any
from datetime import datetime, timezone
import sqlite3


class DBValidator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()

    @contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(self.db_path)
            self._local.connection.row_factory = sqlite3.Row
        try:
            yield self._local.connection
        finally:
            pass  # Connection maintained per thread

    def validate_database(self) -> Dict[str, Any]:
        with self._lock:
            results = {
                "orphaned_tracked_tasks": self.check_orphaned_tracked_tasks(),
                "orphaned_session_tasks": self.check_orphaned_session_tasks(),
                "invalid_task_times": self.validate_task_times(),
                "invalid_session_times": self.validate_session_times(),
                "session_task_consistency": self.check_session_task_consistency(),
                "tracked_task_time_consistency": self.check_tracked_task_time_consistency(),
                "duplicate_active_tasks": self.check_duplicate_active_tasks(),
            }
            return {k: v for k, v in results.items() if v}

    def check_orphaned_tracked_tasks(self) -> List[Dict[str, Any]]:
        """Find tracked tasks referencing non-existent tasks."""
        with self._get_connection() as conn:
            return [
                dict(row)
                for row in conn.execute(
                    """
                SELECT tt.* FROM tracked_tasks tt
                LEFT JOIN tasks t ON tt.task_id = t.id
                WHERE t.id IS NULL
            """
                ).fetchall()
            ]

    def check_orphaned_session_tasks(self) -> List[Dict[str, Any]]:
        """Find session tasks referencing non-existent tasks."""
        with self._get_connection() as conn:
            orphaned = []
            sessions = conn.execute("SELECT id, tasks FROM sessions").fetchall()
            for session in sessions:
                if not session["tasks"]:
                    continue
                task_ids = session["tasks"]  # Assuming tasks is stored as JSON
                for task_id in task_ids:
                    if not conn.execute(
                        "SELECT 1 FROM tasks WHERE id = ?", (task_id,)
                    ).fetchone():
                        orphaned.append(
                            {"session_id": session["id"], "invalid_task_id": task_id}
                        )
            return orphaned

    def validate_task_times(self) -> List[Dict[str, Any]]:
        """Check for invalid task timestamps."""
        with self._get_connection() as conn:
            return [
                dict(row)
                for row in conn.execute(
                    """
                SELECT * FROM tasks 
                WHERE created_at > updated_at 
                OR created_at > datetime('now') 
                OR updated_at > datetime('now')
            """
                ).fetchall()
            ]

    def validate_session_times(self) -> List[Dict[str, Any]]:
        """Check for invalid session timestamps and durations."""
        with self._get_connection() as conn:
            return [
                dict(row)
                for row in conn.execute(
                    """
                SELECT * FROM sessions 
                WHERE (end_time IS NOT NULL AND start_time > end_time)
                OR start_time > datetime('now')
                OR (end_time IS NOT NULL AND end_time > datetime('now'))
                OR created_at > updated_at
            """
                ).fetchall()
            ]

    def check_session_task_consistency(self) -> List[Dict[str, Any]]:
        """Verify consistency between sessions and their tracked tasks."""
        with self._get_connection() as conn:
            inconsistencies = []
            sessions = conn.execute(
                """
                SELECT s.*, GROUP_CONCAT(tt.task_id) as tracked_task_ids
                FROM sessions s
                LEFT JOIN tracked_tasks tt ON s.id = tt.session_id
                GROUP BY s.id
            """
            ).fetchall()

            for session in sessions:
                if session["tasks"]:  # Tasks listed in session
                    tracked_ids = (
                        set(map(int, session["tracked_task_ids"].split(",")))
                        if session["tracked_task_ids"]
                        else set()
                    )
                    session_ids = set(session["tasks"])
                    if tracked_ids != session_ids:
                        inconsistencies.append(
                            {
                                "session_id": session["id"],
                                "session_tasks": list(session_ids),
                                "tracked_tasks": list(tracked_ids),
                                "type": "mismatched_tasks",
                            }
                        )
            return inconsistencies

    def check_tracked_task_time_consistency(self) -> List[Dict[str, Any]]:
        """Verify tracked task time calculations are consistent."""
        with self._get_connection() as conn:
            inconsistencies = []
            tracked_tasks = conn.execute(
                """
                SELECT tt.*, t.time_spent as task_total_time
                FROM tracked_tasks tt
                JOIN tasks t ON tt.task_id = t.id
                WHERE tt.end_time IS NOT NULL
            """
            ).fetchall()

            for tt in tracked_tasks:
                start = datetime.fromisoformat(tt["start_time"])
                end = datetime.fromisoformat(tt["end_time"])
                calculated_time = int((end - start).total_seconds())
                if abs(calculated_time - tt["time_spent"]) > 1:  # 1 second tolerance
                    inconsistencies.append(
                        {
                            "tracked_task_id": tt["id"],
                            "task_id": tt["task_id"],
                            "recorded_time": tt["time_spent"],
                            "calculated_time": calculated_time,
                            "type": "time_mismatch",
                        }
                    )
            return inconsistencies

    def check_duplicate_active_tasks(self) -> List[Dict[str, Any]]:
        """Find tasks that are marked as active multiple times."""
        with self._get_connection() as conn:
            return [
                dict(row)
                for row in conn.execute(
                    """
                SELECT task_id, COUNT(*) as count
                FROM tracked_tasks
                WHERE end_time IS NULL
                GROUP BY task_id
                HAVING count > 1
            """
                ).fetchall()
            ]

    def fix_orphaned_records(self) -> Dict[str, int]:
        """Attempt to fix orphaned records."""
        with self._get_connection() as conn:
            tracked_deleted = conn.execute(
                """
                DELETE FROM tracked_tasks 
                WHERE task_id NOT IN (SELECT id FROM tasks)
            """
            ).rowcount

            sessions = conn.execute("SELECT id, tasks FROM sessions").fetchall()
            session_updates = 0
            for session in sessions:
                if not session["tasks"]:
                    continue
                valid_tasks = [
                    task_id
                    for task_id in session["tasks"]
                    if conn.execute(
                        "SELECT 1 FROM tasks WHERE id = ?", (task_id,)
                    ).fetchone()
                ]
                if len(valid_tasks) != len(session["tasks"]):
                    conn.execute(
                        "UPDATE sessions SET tasks = ? WHERE id = ?",
                        (valid_tasks, session["id"]),
                    )
                    session_updates += 1

            return {
                "tracked_tasks_deleted": tracked_deleted,
                "sessions_updated": session_updates,
            }
