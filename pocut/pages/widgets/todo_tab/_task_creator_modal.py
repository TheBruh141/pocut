from datetime import datetime
from typing import Optional

from textual import events
from textual.app import ComposeResult
from textual.containers import Container, HorizontalScroll, Center
from textual.screen import ModalScreen
from textual.widgets import Label, Static, Input, Select, Checkbox, Button

from pocut.pages.widgets.common import SmallButton
from pocut.utils import task as t
from pocut.utils.taskmanager import handle_data_create_headless


class TaskCreatorModal(ModalScreen[bool]):
    """
    A modal screen for creating tasks with customizable attributes.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the layout for the Task Creator modal screen.
        """
        with Container():
            yield Static("Task Title:")
            yield Input(placeholder="Enter task title", id="task-title")

            yield Static("Task Description:")
            yield Input(placeholder="Enter task description", id="task-text")

            yield Static("Priority:")
            yield Select(
                options=[
                    ("Low", "1"),
                    ("Medium", "2"),
                    ("High", "3"),
                ],
                id="task-priority",
                allow_blank=False,
                value="1",
            )

            yield Static("Due Date (YYYY-MM-DD):")
            yield Input(placeholder="Enter due date", id="task-due-date")

            yield Static("Days of the Week:")
            yield Input(
                placeholder="Comma-separated days, e.g., Mon, Tue",
                id="task-days-of-week",
            )

            with HorizontalScroll():
                yield Checkbox(
                    label="Completed",
                    id="task-completed",
                    tooltip="Mark the task as completed",
                )

                yield Checkbox(
                    label="Daily",
                    id="task-is-daily",
                    tooltip="Set the task as a daily recurring task",
                )
                yield Checkbox(
                    label="Weekly",
                    id="task-is-weekly",
                    tooltip="Set the task as a weekly recurring task",
                )
                yield Checkbox(
                    label="Monthly",
                    id="task-is-monthly",
                    tooltip="Set the task as a monthly recurring task",
                )
                yield Checkbox(
                    label="Yearly",
                    id="task-is-yearly",
                    tooltip="Set the task as a yearly recurring task",
                )

            yield Center(SmallButton(label="Create Task", id="create-task"))

    def get_task_data(self) -> t.Task:
        """
        Collect data from the input fields and return it as a Task object.

        Returns:
            t.Task: Task object with the collected data.
        """
        title: str = self.query_one("#task-title", Input).value.strip()
        text: str = self.query_one("#task-text", Input).value.strip()
        priority_input: Optional[str] = self.query_one("#task-priority", Select).value
        due_date_input: Optional[str] = self.query_one(
            "#task-due-date", Input
        ).value.strip()
        days_of_week_input: Optional[str] = self.query_one(
            "#task-days-of-week", Input
        ).value.strip()

        # Sanitize and validate input
        title = title or "Empty Task"
        text = (
            text
            or "This task was created automatically because you didn't provide details!"
        )

        try:
            priority: int = int(priority_input) if priority_input else 1
        except:
            self.notify(
                "Priority must be a number between 1 and 3.",
                title="Invalid Priority",
                severity="error",
            )
            priority = 1

        try:
            due_date: Optional[datetime] = (
                datetime.strptime(due_date_input, "%Y-%m-%d")
                if due_date_input
                else None
            )
        except ValueError:
            self.notify(
                "Invalid date format. Please use YYYY-MM-DD.",
                title="Invalid Due Date",
                severity="error",
            )
            due_date = None

        days_of_week: list[str] = [
            day.strip().capitalize()
            for day in days_of_week_input.split(",")
            if days_of_week_input
        ]

        return t.Task(
            title=title,
            text=text,
            priority=priority,
            due_date=due_date,
            completed=self.query_one("#task-completed", Checkbox).value,
            is_daily=self.query_one("#task-is-daily", Checkbox).value,
            is_weekly=self.query_one("#task-is-weekly", Checkbox).value,
            is_monthly=self.query_one("#task-is-monthly", Checkbox).value,
            is_yearly=self.query_one("#task-is-yearly", Checkbox).value,
            days_of_week=days_of_week,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle the button press event to create a task.

        Args:
            event (Button.Pressed): The button press event.
        """
        if event.button.id == "create-task":
            task_data = self.get_task_data()

            handle_data_create_headless(task_data)
            self.dismiss(True)

    def on_key(self, event: events.Key) -> None:
        """
        Handle the escape key to close the modal screen.

        Args:
            event (events.Key): The key event.
        """
        if event.key == "escape":
            self.dismiss(False)
