# from datetime import datetime
# from typing import Optional
#
# from textual import events
# from textual.app import ComposeResult
# from textual.containers import Container, Horizontal, Vertical, HorizontalScroll
# from textual.events import Event
# from textual.widget import Widget
# from textual.widgets import (
#     Static,
#     Label,
#     Digits,
#     TextArea,
#     Button,
#     Input,
#     Select,
#     Checkbox,
# )
# import pocut.utils.task as t
# from pocut import AppState
# from pocut.utils import PomodoroDB, Task
#
#
# class TodoTask(Container, can_focus=True):
#     # Note for the wizards that have decided to edit this.
#     # we can't have a property named self.task because
#     # textual already has a property named task.
#     def __init__(self, task: t.Task, **kwargs):
#         super().__init__(**kwargs)
#         self.info = task
#
#     def compose(self) -> ComposeResult:
#         with Horizontal():
#             with Vertical():
#                 yield Label(self.info.title + "\n")
#                 yield Label(self.info.text)
#
#             yield Label(
#                 f"[{"Completed" if self.info.completed else "Not completed"}]",
#                 id="status",
#                 variant="success" if self.info.completed else "accent",
#             )
#             yield Digits(self.info.priority.__str__())
#
#
# class TaskCreator(Static):
#     """
#     A widget for creating tasks with customizable attributes.
#     """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def compose(self) -> ComposeResult:
#         """
#         Compose the layout for the Task Creator widget.
#         """
#         with Container():
#             yield Static("Task Title:")
#             yield Input(placeholder="Enter task title", id="task-title")
#
#             yield Static("Task Description:")
#             yield Input(placeholder="Enter task description", id="task-text")
#
#             yield Static("Priority:")
#             yield Select(
#                 options=[
#                     ("Low", "1"),
#                     ("Medium", "2"),
#                     ("High", "3"),
#                 ],
#                 id="task-priority",
#             )
#
#             yield Static("Due Date (YYYY-MM-DD):")
#             yield Input(placeholder="Enter due date", id="task-due-date")
#
#             with HorizontalScroll():
#                 yield Checkbox(label="Completed", id="task-completed")
#
#                 yield Checkbox(label="Daily", id="task-is-daily")
#                 yield Checkbox(label="Weekly", id="task-is-weekly")
#                 yield Checkbox(label="Monthly", id="task-is-monthly")
#                 yield Checkbox(label="Yearly", id="task-is-yearly")
#
#             yield Static("Days of the Week:")
#             yield Input(
#                 placeholder="Comma-separated days, e.g., Mon, Tue",
#                 id="task-days-of-week",
#             )
#
#             yield Button(label="Create Task", id="create-task")
#
#     def get_task_data(self) -> t.Task:
#         """
#         Collect data from the input fields and return it as a Task object.
#
#         Returns:
#             t.Task: Task object with the collected data.
#         """
#         title: str = self.query_one("#task-title", Input).value or "Untitled Task"
#         text: str = self.query_one("#task-text", Input).value or ""
#         priority: int = int(self.query_one("#task-priority", Select).value or 1)
#         due_date_input: Optional[str] = self.query_one("#task-due-date", Input).value
#         try:
#             due_date: Optional[datetime] = (
#                 datetime.strptime(due_date_input, "%Y-%m-%d")
#                 if due_date_input
#                 else None
#             )
#         except ValueError:
#             self.notify(
#                 "setting it to None",
#                 title="Invalid due date",
#                 severity="error",
#             )
#             due_date = None  # Invalid date format
#         completed: bool = self.query_one("#task-completed", Checkbox).value
#         is_daily: bool = self.query_one("#task-is-daily", Checkbox).value
#         is_weekly: bool = self.query_one("#task-is-weekly", Checkbox).value
#         is_monthly: bool = self.query_one("#task-is-monthly", Checkbox).value
#         is_yearly: bool = self.query_one("#task-is-yearly", Checkbox).value
#         days_of_week: list[str] = [
#             day.strip()
#             for day in (
#                 self.query_one("#task-days-of-week", Input).value.split(",")
#                 if self.query_one("#task-days-of-week", Input).value
#                 else []
#             )
#         ]
#
#         return t.Task(
#             title=title,
#             text=text,
#             priority=priority,
#             due_date=due_date,
#             completed=completed,
#             is_daily=is_daily,
#             is_weekly=is_weekly,
#             is_monthly=is_monthly,
#             is_yearly=is_yearly,
#             days_of_week=days_of_week,
#             created_at=datetime.now(),
#             updated_at=datetime.now(),
#         )
#
#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         """
#         Handle the button press event to create a task.
#
#         Args:
#             event (Button.Pressed): The button press event.
#         """
#         if event.button.id == "create-task":
#             task_data = self.get_task_data()
#             self.post_message(t.TaskData(task_data))
#
#
# class TodoTab(Static):
#
#     db: PomodoroDB
#
#     def __init__(self, state: AppState):
#         super().__init__()
#         self.state = state
#         self.db = PomodoroDB()
#         self.task_widgets = []
#         self.focused_index = 0
#
#     def compose(self) -> ComposeResult:
#         yield TaskCreator()
#
#         # for debugging
#         # yield Label("random tasks\n\n")
#
#         # for task in t.create_random_tasks(10):
#         #     task_widget = TodoTask(task)
#         #     self.task_widgets.append(task_widget)
#         #     yield task_widget
#         # for task in self.db.list_tasks():
#         #     task_widget = TodoTask(task)
#         #     self.task_widgets.append(task_widget)
#         #     yield task_widget
#
#     def _on_key(self, event: events.Key) -> None:
#         if not self.task_widgets:
#             return
#
#         if event.key == "down":
#             # Move focus to the next task
#             self.focused_index = (self.focused_index + 1) % len(self.task_widgets)
#             self.task_widgets[self.focused_index].focus()
#
#         elif event.key == "up":
#             # Move focus to the previous task
#             self.focused_index = (self.focused_index - 1) % len(self.task_widgets)
#             self.task_widgets[self.focused_index].focus()


from datetime import datetime
from typing import Optional

from textual import events
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, HorizontalScroll, Center
from textual.widgets import (
    Static,
    Label,
    Digits,
    Button,
    Input,
    Select,
    Checkbox,
)
import pocut.utils.task as t
from pocut import AppState
from pocut.utils import PomodoroDB
from textual.screen import ModalScreen


class TodoTask(Container, can_focus=True):
    # Note for the wizards that have decided to edit this.
    # we can't have a property named self.task because
    # textual already has a property named task.
    def __init__(self, task: t.Task, **kwargs):
        super().__init__(**kwargs)
        self.info = task

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical():
                yield Label(self.info.title + "\n")
                yield Label(self.info.text)

            yield Label(
                f"[{'Completed' if self.info.completed else 'Not completed'}]",
                id="status",
                variant="success" if self.info.completed else "accent",
            )
            yield Digits(self.info.priority.__str__())


class TaskCreatorModal(ModalScreen):
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

            yield Center(Button(label="Create Task", id="create-task"))

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
            self.post_message(t.TaskData(task_data))
            self.dismiss()

    def on_key(self, event: events.Key) -> None:
        """
        Handle the escape key to close the modal screen.

        Args:
            event (events.Key): The key event.
        """
        if event.key == "escape":
            self.dismiss()


class TodoTab(Static):

    db: PomodoroDB

    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        self.db = PomodoroDB()
        self.task_widgets = []
        self.focused_index = 0

    def compose(self) -> ComposeResult:
        yield Button(label="Add Task", id="add-task")

        # for debugging
        # yield Label("random tasks\n\n")

        # for task in t.create_random_tasks(10):
        #     task_widget = TodoTask(task)
        #     self.task_widgets.append(task_widget)
        #     yield task_widget
        # for task in self.db.list_tasks():
        #     task_widget = TodoTask(task)
        #     self.task_widgets.append(task_widget)
        #     yield task_widget

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button presses in the TodoTab.

        Args:
            event (Button.Pressed): The button press event.
        """
        if event.button.id == "add-task":
            self.app.push_screen(TaskCreatorModal())

    def _on_key(self, event: events.Key) -> None:
        if not self.task_widgets:
            return

        if event.key == "down":
            # Move focus to the next task
            self.focused_index = (self.focused_index + 1) % len(self.task_widgets)
            self.task_widgets[self.focused_index].focus()

        elif event.key == "up":
            # Move focus to the previous task
            self.focused_index = (self.focused_index - 1) % len(self.task_widgets)
            self.task_widgets[self.focused_index].focus()
