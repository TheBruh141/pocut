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
        - ongoing: Whether the task is ongoing.
        - priority: Priority level of the task (default is 1, higher means more important).
        - category_id: ID of the category this task belongs to (optional).
        - attempts: Number of Pomodoro attempts made for this task.
        - time_spent: Total time spent on this task (in minutes).
        - due_date: Optional due date for the task.
        - is_daily, is_weekly, is_monthly, is_yearly: Flags for recurring tasks.
        - days_of_week: Specific days of the week the task is active (e.g., ["Monday", "Wednesday"]).
        - created_at: Timestamp when the task was created.
        - updated_at: Timestamp when the task was last updated.

    Notes:
        Please be sure that a session can not be ongoing and done at the same time.
    """

    id: Optional[int] = None
    title: str = "Untitled Task"
    text: str = ""
    completed: bool = False
    ongoing: bool = False
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
    """
    Represents a collection of events related to a Task.

    Attributes:
        task (Task): The task associated with the event.
    """

    bubble = True
    # Note from Bruh.
    # We are using different subclasses for different
    # actions because it's easier to manage.

    def __init__(self, _task: Task):
        """
        Initializes the TaskData event with a task.

        Args:
            _task (Task): The task associated with this event.
        """
        super().__init__()
        self.task: Task = _task

    class Delete(Event):
        """
        Represents a delete event for a Task.
        """

        def __init__(self, _task: Task):
            """
            Initializes the Delete event with a task.

            Args:
                _task (Task): The task to be deleted.
            """
            super().__init__()
            self.task: Task = _task

    class Update(Event):
        """
        Represents an update event for a Task.
        """

        def __init__(self, _task: Task):
            """
            Initializes the Update event with a task.

            Args:
                _task (Task): The task to be updated.
            """
            super().__init__()
            self.task: Task = _task

    class Create(Event):
        """
        Represents a create event for a Task.
        """

        def __init__(self, _task: Task):
            """
            Initializes the Create event with a task.

            Args:
                _task (Task): The task to be created.
            """
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
