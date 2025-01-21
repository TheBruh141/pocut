from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import rich.repr
from textual.events import Event


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
    text: str = "No Description Given"
    completed: bool = False
    ongoing: bool = False
    priority: int = 1
    category_id: Optional[int] = None
    attempts: int = 0
    time_spent: float = 0
    due_date: Optional[datetime] = None
    is_daily: bool = False
    is_weekly: bool = False
    is_monthly: bool = False
    is_yearly: bool = False
    days_of_week: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return (
            self.id == other.id
            and self.title == other.title
            and self.text == other.text
            and self.completed == other.completed
            and self.ongoing == other.ongoing
            and self.priority == other.priority
            and self.category_id == other.category_id
            and self.attempts == other.attempts
            and self.time_spent == other.time_spent
            and self.due_date == other.due_date
            and self.is_daily == other.is_daily
            and self.is_weekly == other.is_weekly
            and self.is_monthly == other.is_monthly
            and self.is_yearly == other.is_yearly
            and self.days_of_week == other.days_of_week
            and self.created_at == other.created_at
            and self.updated_at == other.updated_at
        )

    def modify(self, updates: dict[str, any]):
        """
        Modifies the task's attributes based on the provided updates.

        Args:
            - updates: A dictionary where keys are the attribute names and values are the new values.
        """
        for key, value in updates.items():
            if hasattr(self, key):  # Check if the attribute exists in the Task class
                setattr(self, key, value)
            else:
                raise AttributeError(f"Task has no attribute '{key}'")

        # Ensure the `updated_at` field is always updated when any modification happens.
        self.updated_at = datetime.now()

    @classmethod
    def from_dict(cls, data: dict, is_tracked: bool = False) -> "Task":
        """
        Create a Task instance from a dictionary.

        Args:
            data: A dictionary containing Task attributes.

        Returns:
            Task: An instance of Task.
        """
        try:
            return cls(
                id=data.get("id") if not is_tracked else data.get("task_id"),
                title=data.get("title", "Untitled Task"),
                text=data.get("text", "No Description Given"),
                completed=data.get("completed", False),
                ongoing=data.get("ongoing", False),
                priority=data.get("priority", 1),
                category_id=data.get("category_id"),
                attempts=data.get("attempts", 0),
                time_spent=data.get("time_spent", 0),
                due_date=data.get("due_date"),
                is_daily=data.get("is_daily", False),
                is_weekly=data.get("is_weekly", False),
                is_monthly=data.get("is_monthly", False),
                is_yearly=data.get("is_yearly", False),
                days_of_week=data.get("days_of_week", []),
                created_at=data.get("created_at", datetime.now()),
                updated_at=data.get("updated_at", datetime.now()),
            )

        # Error messages
        except KeyError as e:
            raise KeyError(
                f"Task has no attribute '{e.args[0]}'.\n"
                f"If you are not a developer, please report this error to\n"
                f"https://github.com/TheBruh141/pocut"
                f"Sorry for any disturbances"
            ) from e

        except Exception as e:
            raise Exception(
                "Task error. Task seems to be malformed"
                f"If you are not a developer, please report this error to\n"
                f"https://github.com/TheBruh141/pocut"
                f"Sorry for any disturbances"
            ) from e


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

    class Complete(Event):
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
