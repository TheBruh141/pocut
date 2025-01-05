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

import textual.widget
from textual import events, on, work
from textual.app import ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    Vertical,
    HorizontalScroll,
    Center,
    Right,
    ScrollableContainer,
)
from textual.events import DescendantBlur, Focus, Blur, DescendantFocus
from textual.reactive import await_watcher
from textual.widgets import (
    Static,
    Label,
    Digits,
    Button,
    Input,
    Select,
    Checkbox,
    Footer,
)
import pocut.utils.task as t
from pocut import AppState
from pocut.utils import PomodoroDB
from textual.screen import ModalScreen, Screen

from pocut.utils.taskmanager import handle_data_create_headless
from pocut.widgets.common.custom_button import SmallButton


class TodoTask(Container, can_focus=True):
    # Note for the wizards that have decided to edit this.
    # we can't have a property named self.task because
    # textual already has a property named task.

    def __init__(self, task: t.Task, **kwargs):
        super().__init__(**kwargs)
        self.info = task

    def compose(self) -> ComposeResult:
        with Horizontal(id="task-cluster"):
            with Vertical():
                yield Label(self.info.title + "\n", id="title")
                yield Label(self.info.text, id="text")

            with Horizontal(id="task-status"):
                yield SmallButton("edit", classes="status")
                yield SmallButton(
                    "\[x]" if self.info.completed == True else "[ ]",
                    id="complete-button",
                    # variant="success" if self.info.completed else "accent",
                    classes="completed" if self.info.completed else "not-completed",
                )
            # yield Digits(self.info.priority.__str__())

    @on(events.DescendantFocus)
    async def handle_complete_button_focus(self, event: DescendantFocus):

        if event.widget.id != "complete-button":
            self.notify(event.widget.__str__())
            return
        btn = self.query_one("#complete-button", Button)
        btn.label = "\[x]"

    @on(events.DescendantBlur)
    def handle_complete_button_blur(self, event: DescendantBlur):
        if event.widget.id != "complete-button":
            return
        btn = self.query_one("#complete-button", Button)
        btn.label = "[ ]"

    @on(events.Key)
    def handle_interactions(self, e: events.Key) -> None:
        # if e.key == "l":
        #     # this might seem weird but this is a actually a breakpoint. so if something goes
        #     # wrong I'll just be using this
        #     print("kaboom")
        pass


class TaskCreatorModal(ModalScreen[bool]):
    """
    A modal screen for creating tasks with customizable attributes.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the layout for the Task Creator modal screen.
        """
        with Container():
            yield Label(f"parent: {self.parent}")
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

    def on_mount(self):
        self.notify("mounted")

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


class TodoTab(Container):
    _inherit_bindings = False
    _merged_bindings = False
    BINDINGS = [
        ("a", "create_task", "create task"),
        ("d", "delete_task", "delete task"),
        ("e", "edit_task", "edit task"),
    ]
    db: PomodoroDB

    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        self.db = PomodoroDB()
        self.task_widgets = []
        self.focused_index = 0

    def on_mount(self):

        for w in self.children:
            w.border_title = f"{w.id if w.id else "NO FUCKGIN NAME"}"

        self.recompose()

    def compose(self) -> ComposeResult:
        with Horizontal(id="todo-tab-button-cluster"):
            yield SmallButton(label="Add Task", id="add-task")

            with Right():
                yield SmallButton(label="Edit", id="edit-task")

        with ScrollableContainer(can_focus=False, can_focus_children=True):
            for task in self.db.list_tasks():
                task_widget = TodoTask(task)
                self.task_widgets.append(task_widget)
                yield task_widget

        yield Footer()

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button presses in the TodoTab.

        Args:
            event (Button.Pressed): The button press event.
        """
        if event.button.id == "add-task":
            await self.app.push_screen(TaskCreatorModal(), wait_for_dismiss=True)
            self.refresh(repaint=True, recompose=True, layout=True)

    # Handle task creation
    @on(t.TaskData.Create)
    def handle_data_create(self, data: t.TaskData) -> None:
        """
        Handles the creation of a new task by inserting it into the database.

        Args:
            data (t.TaskData): Event data containing the task to create.
        """
        db = PomodoroDB()
        self.notify("Creating new task...")

        try:
            task_id = db.add_task(data.task)
            print(f"Task created with ID: {task_id}")
        except Exception as e:
            print(f"Error creating task: {e}")

    # Handle task updates
    @on(t.TaskData.Update)
    def handle_data_update(self, data: t.TaskData) -> None:
        """
        Handles updating an existing task in the database.

        Args:
            data (t.TaskData): Event data containing the task to update.
        """
        db = PomodoroDB()
        self.notify("Updating task...")

        try:
            data.task.updated_at = datetime.now()
            db.update_task(data.task)
            print(f"Task with ID {data.task.id} updated.")
        except Exception as e:
            print(f"Error updating task: {e}")

    # Handle task deletion
    @on(t.TaskData.Delete)
    def handle_data_delete(self, data: t.TaskData) -> None:
        """
        Handles deleting a task from the database.

        Args:
            data (t.TaskData): Event data containing the task to delete.
        """
        db = PomodoroDB()
        self.notify("Deleting task...")
        try:
            db.delete_task(data.task.id)
            print(f"Task with ID {data.task.id} deleted.")
        except Exception as e:
            print(f"Error deleting task: {e}")
