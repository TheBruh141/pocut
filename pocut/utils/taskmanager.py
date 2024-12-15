import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    id: Optional[int] = None
    title: str = "Untitled Task"
    text: str = ""
    completed: bool = False
    priority: int = 1
    category_id: Optional[int] = None
    attempts: int = 0
    time_spent: int = 0
    due_date: Optional[datetime] = None
    is_daily: bool = False
    is_weekly: bool = False
    is_monthly: bool = False
    is_yearly: bool = False
    days_of_week: Optional[List[str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class TaskManager:

    def __init__(self, db_path="../db/test.sqlite"):
        self.db_path = Path(db_path)
        self.connection = None
        self._ensure_database()

    def _connect(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row

    def _ensure_database(self):
        self._connect()
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    priority INTEGER CHECK(priority BETWEEN 1 AND 5) DEFAULT 1,
                    category_id INTEGER,
                    attempts INTEGER DEFAULT 0,
                    time_spent INTEGER DEFAULT 0,
                    due_date DATETIME,
                    is_daily BOOLEAN DEFAULT 0,
                    is_weekly BOOLEAN DEFAULT 0,
                    is_monthly BOOLEAN DEFAULT 0,
                    is_yearly BOOLEAN DEFAULT 0,
                    days_of_week TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                );
                """
            )

    def add_task(self, task: Task):
        """
        Add a new task to the database.

        Args:
            task (Task): Task object containing task details.
        """
        self._connect()
        days_of_week_str = ",".join(task.days_of_week) if task.days_of_week else None
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO tasks (title, text, completed, priority, category_id, attempts, time_spent, due_date, 
                                   is_daily, is_weekly, is_monthly, is_yearly, days_of_week, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    task.title,
                    task.text,
                    task.completed,
                    task.priority,
                    task.category_id,
                    task.attempts,
                    task.time_spent,
                    task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
                    task.is_daily,
                    task.is_weekly,
                    task.is_monthly,
                    task.is_yearly,
                    days_of_week_str,
                    task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    task.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            task.id = cursor.lastrowid

    def process_repeated_tasks(self):
        """
        Generate new tasks for repeated tasks based on their interval and settings.
        """
        self._connect()
        now = datetime.now()
        with self.connection:
            tasks = self.connection.execute(
                """
                SELECT * FROM tasks
                WHERE completed = 0 AND 
                      (is_daily = 1 OR is_weekly = 1 OR is_monthly = 1 OR is_yearly = 1);
                """
            ).fetchall()

            for task_row in tasks:
                task = self._row_to_task(task_row)
                new_due_date = self._calculate_next_due_date(task.due_date, task)

                if new_due_date:
                    new_task = Task(
                        title=task.title,
                        text=task.text,
                        priority=task.priority,
                        due_date=new_due_date,
                        is_daily=task.is_daily,
                        is_weekly=task.is_weekly,
                        is_monthly=task.is_monthly,
                        is_yearly=task.is_yearly,
                        days_of_week=task.days_of_week,
                        category_id=task.category_id
                    )
                    self.add_task(new_task)

    def _calculate_next_due_date(self, due_date: Optional[datetime], task: Task) -> Optional[datetime]:
        """
        Calculate the next due date based on the task's interval settings.

        Args:
            due_date (datetime): Current due date.
            task (Task): Task details.

        Returns:
            datetime: Next due date.
        """
        if task.is_daily:
            return due_date + timedelta(days=1) if due_date else datetime.now() + timedelta(days=1)
        if task.is_weekly:
            return self._get_next_weekly_date(due_date, task.days_of_week)
        if task.is_monthly:
            return due_date + timedelta(days=30) if due_date else datetime.now() + timedelta(days=30)
        if task.is_yearly:
            return due_date + timedelta(days=365) if due_date else datetime.now() + timedelta(days=365)
        return None

    def _get_next_weekly_date(self, due_date: Optional[datetime], days_of_week: List[str]) -> Optional[datetime]:
        """
        Calculate the next date for a weekly repeated task.

        Args:
            due_date (datetime): Current due date.
            days_of_week (list[str]): Days of the week (e.g., ["Monday", "Wednesday"]).

        Returns:
            datetime: Next applicable date.
        """
        if not days_of_week:
            return None

        today = datetime.now()
        if due_date and due_date > today:
            today = due_date

        for i in range(7):
            next_date = today + timedelta(days=i)
            if next_date.strftime("%A") in days_of_week:
                return next_date

        return None

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """
        Convert a database row to a Task object.

        Args:
            row (sqlite3.Row): Row fetched from the database.

        Returns:
            Task: Task object.
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
            due_date=datetime.strptime(row["due_date"], "%Y-%m-%d") if row["due_date"] else None,
            is_daily=bool(row["is_daily"]),
            is_weekly=bool(row["is_weekly"]),
            is_monthly=bool(row["is_monthly"]),
            is_yearly=bool(row["is_yearly"]),
            days_of_week=row["days_of_week"].split(",") if row["days_of_week"] else [],
            created_at=datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.strptime(row["updated_at"], "%Y-%m-%d %H:%M:%S")
        )

    def get_tasks(self) -> List[Task]:
        """
        Retrieve all tasks from the database.

        Returns:
            list[Task]: List of tasks.
        """
        self._connect()
        with self.connection:
            tasks = self.connection.execute("SELECT * FROM tasks;").fetchall()
        return [self._row_to_task(task) for task in tasks]

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_all_tasks(self):
        """
        Retrieve all tasks from the database.

        Returns:
            List[Task]: A list of Task objects representing all tasks in the database.
        """
        tasks = []
        try:
            # Assuming `self.connection` is a valid SQLite connection
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id, title, text, priority, due_date, is_daily, is_weekly, is_monthly, is_yearly FROM tasks")
            rows = cursor.fetchall()

            for row in rows:
                tasks.append(Task(
                    id=row[0],
                    title=row[1],
                    text=row[2],
                    priority=row[3],
                    due_date=row[4],
                    is_daily=row[5],
                    is_weekly=row[6],
                    is_monthly=row[7],
                    is_yearly=row[8],
                ))
        except Exception as e:
            print(f"Error retrieving tasks: {e}")

        return tasks


# Example Usage
if __name__ == "__main__":
    manager = TaskManager()

    # Add tasks
    daily_task = Task(
        title="Daily task example",
        text="Example of a daily repeated task",
        priority=3,
        is_daily=True
    )
    manager.add_task(daily_task)

    weekly_task = Task(
        title="Weekly task",
        text="Weekly task for Monday and Wednesday",
        priority=5,
        is_weekly=True,
        days_of_week=["Monday", "Wednesday"]
    )
    manager.add_task(weekly_task)

    # Process repeated tasks
    manager.process_repeated_tasks()

    # Retrieve tasks
    tasks = manager.get_tasks()
    print("Tasks:")
    for task in tasks:
        print(task)

    manager.close()
