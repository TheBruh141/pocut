from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from faker import Faker
import rich.repr
from textual.events import Event

fake = Faker()


@rich.repr.auto
@dataclass
class Task:
    """
    Represents a task in the Pomodoro app.

    Attributes:
        - id: Unique identifier for the task (assigned automatically by the database).
        - title: Title of the task.
        - text: Description or notes related to the task.
        - completed: Whether the task is completed.
        - priority: Priority level of the task (default is 1, higher means more important).
        - category_id: ID of the category this task belongs to (optional).
        - attempts: Number of Pomodoro attempts made for this task.
        - time_spent: Total time spent on this task (in minutes).
        - due_date: Optional due date for the task.
        - is_daily, is_weekly, is_monthly, is_yearly: Flags for recurring tasks.
        - days_of_week: Specific days of the week the task is active (e.g., ["Monday", "Wednesday"]).
        - created_at: Timestamp when the task was created.
        - updated_at: Timestamp when the task was last updated.
    """

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
    days_of_week: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class TaskData(Event):
    def __init__(self, _task: Task):
        super().__init__()
        self.task: Task = _task


@rich.repr.auto
@dataclass
class Session:
    """
    Represents a Pomodoro session, which can include multiple tasks.

    Attributes:
        - id: Unique identifier for the session (assigned automatically by the database).
        - start_time: When the session started.
        - end_time: When the session ended (optional if session is ongoing).
        - tasks: List of task IDs completed or worked on during this session.
        - completed: Whether the session was completed successfully.
        - created_at: Timestamp when the session was created.
        - updated_at: Timestamp when the session was last updated.
    """

    id: Optional[int] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    tasks: list[int] = field(default_factory=list)  # List of task IDs
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


import random
from datetime import timedelta

# Extend Task and Session to allow for random generation.


def create_random_tasks(num_tasks: int) -> list[Task]:
    """
    Generate a list of realistic tasks using Faker for more lifelike data.

    Args:
        num_tasks (int): Number of random tasks to generate.

    Returns:
        list[Task]: A list of realistically generated Task objects.
    """
    categories = [None, 1, 2, 3]  # Example categories
    priorities = [1, 2, 3, 4, 5]  # Example priority levels
    task_list = []

    for i in range(num_tasks):
        task = Task(
            id=i + 1,
            title=fake.sentence(nb_words=4).rstrip("."),
            text=fake.text(max_nb_chars=100),
            completed=random.choice([True, False]),
            priority=random.choice(priorities),
            category_id=random.choice(categories),
            attempts=random.randint(0, 10),
            time_spent=random.randint(0, 240),
            due_date=(
                fake.date_time_between(start_date="now", end_date="+30d")
                if random.choice([True, False])
                else None
            ),
            is_daily=random.choice([True, False]),
            is_weekly=random.choice([True, False]),
            is_monthly=random.choice([True, False]),
            is_yearly=random.choice([True, False]),
            days_of_week=random.sample(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
                k=random.randint(0, 7),
            ),
        )
        task_list.append(task)

    return task_list


def create_random_sessions(num_sessions: int, task_pool: list[Task]) -> list[Session]:
    """
    Generate a list of realistic sessions using a given pool of tasks.

    Args:
        num_sessions (int): Number of random sessions to generate.
        task_pool (list[Task]): A list of tasks to randomly associate with sessions.

    Returns:
        list[Session]: A list of realistically generated Session objects.
    """
    sessions = []

    for i in range(num_sessions):
        num_tasks_in_session = random.randint(1, len(task_pool))
        session_tasks = random.sample(
            [task.id for task in task_pool], k=num_tasks_in_session
        )

        start_time = fake.date_time_between(start_date="-48h", end_date="now")
        end_time = (
            start_time + timedelta(minutes=random.randint(25, 240))
            if random.choice([True, False])
            else None
        )

        session = Session(
            id=i + 1,
            start_time=start_time,
            end_time=end_time,
            tasks=session_tasks,
            completed=random.choice([True, False]),
        )
        sessions.append(session)

    return sessions


# Example usage
if __name__ == "__main__":
    random_tasks = create_random_tasks(5)
    random_sessions = create_random_sessions(3, random_tasks)

    for task in random_tasks:
        print(task)

    for session in random_sessions:
        print(session)
