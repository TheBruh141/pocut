from datetime import datetime
from typing import Optional

import textual.widget
from rich.markdown import Markdown
from textual import events, on, work, lazy
from textual.app import ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    Vertical,
    HorizontalScroll,
    Center,
    Right,
    ScrollableContainer,
    VerticalScroll,
)
from textual.events import DescendantBlur, Focus, Blur, DescendantFocus
from textual.message import Message
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
    Collapsible,
)
from textual.widgets import Markdown as MarkdownWidget
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

    class Entered(Message, bubble=True):
        def __init__(self, id: int, original: "TodoTask"):
            super().__init__()
            self.id = id
            self.original: TodoTask = original

    def __init__(self, task: t.Task, **kwargs):
        super().__init__(**kwargs)
        self.info = task

    def make_all_disabled(self) -> None:
        for widget in self.walk_children():
            widget.disabled = True

    def compose(self) -> ComposeResult:
        with Horizontal(id="task-cluster", classes="task-card"):
            with Vertical(id="task-card"):
                # Task Title
                yield Label(self.info.title, id="title", classes="title")

                # Task Text
                yield Label(self.info.text, id="text", classes="text")

                # Priority and Status
                with Horizontal(classes="task-metadata"):
                    yield Label(f"Priority: {self.info.priority}", classes="priority")
                    status = (
                        "Completed"
                        if self.info.completed
                        else "Ongoing" if self.info.ongoing else "Pending"
                    )
                    yield Label(
                        f" Status: {status}", classes=f"status-{status.lower()}"
                    )

                # Due Date
                if self.info.due_date:
                    yield Label(
                        f"Due: {self.info.due_date.strftime('%Y-%m-%d')}",
                        classes="due-date",
                    )

            #  implement later
            #         # Collapsible Details Section
            #         with Collapsible(title="Details", classes="details"):
            #             with ScrollableContainer():
            #                 yield MarkdownWidget(
            #                     Markdown(
            #                         f"""\
            # ### Task Details
            # - **ID:** {self.info.id or "N/A"}
            # - **Category ID:** {self.info.category_id or "N/A"}
            # - **Attempts:** {self.info.attempts}
            # - **Time Spent:** {self.info.time_spent} minutes
            # - **Recurring:** {"Yes" if self.info.is_daily or self.info.is_weekly or self.info.is_monthly or self.info.is_yearly else "No"}
            #     - **Daily:** {self.info.is_daily}
            #     - **Weekly:** {self.info.is_weekly}
            #     - **Monthly:** {self.info.is_monthly}
            #     - **Yearly:** {self.info.is_yearly}
            # - **Days of Week:** {", ".join(self.info.days_of_week) if self.info.days_of_week else "None"}
            # - **Created At:** {self.info.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            # - **Updated At:** {self.info.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
            #                         """
            #                     ).__str__()
            #                 )
            with Vertical(id="task-status"):
                # yield SmallButton("edit", classes="edit-button", disabled=True)
                yield SmallButton(
                    "\[x]" if self.info.completed == True else "[ ]",
                    id="complete-button",
                    # variant="success" if self.info.completed else "accent",
                    classes="completed" if self.info.completed else "not-completed",
                    disabled=False,
                    tooltip=Markdown(
                        f"**Press me** to make the task {"complete" if self.info.completed else "incomplete" }.\n"
                        "> Note, you need to press enter to access me "
                    ),
                )
                yield SmallButton(
                    label="Delete",
                    id="delete-button",
                    disabled=False,
                    variant="error",
                )

            # yield Digits(self.info.priority.__str__())

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter" or event.key == "space":
            self.post_message(self.Entered(self.info.id, self))

    @on(Button.Pressed, "#complete-button")
    def handle_complete_button_press(self, event: Button.Pressed):
        self.info.completed = not self.info.completed

        event.button.label = "[ ]" if self.info.completed else "\[x]"
        self.refresh(recompose=True)
        self.post_message(t.TaskData.Update(self.info))
        pass

    @on(Button.Pressed, "#delete-button")
    def handle_delete_button_press(self, event: Button.Pressed):
        self.post_message(t.TaskData.Delete(self.info))
        self.notify(f"deleted {self.info.title}", severity="information")
        self.remove()
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

        # Separate completed and uncompleted tasks
        completed_tasks = [task for task in self.db.list_tasks() if task.completed]
        uncompleted_tasks = [
            task for task in self.db.list_tasks() if not task.completed
        ]
        with ScrollableContainer():
            # Render uncompleted tasks
            if uncompleted_tasks:
                with lazy.Reveal(VerticalScroll(id="uncompleted-tasks-section")):
                    yield Label("Uncompleted Tasks", classes="section-title")
                    for task in uncompleted_tasks:
                        task_widget = TodoTask(task)
                        self.task_widgets.append(task_widget)
                        yield task_widget

            # Render completed tasks
            if completed_tasks:
                with lazy.Reveal(Vertical(id="completed-tasks-section")):
                    yield Label("Completed Tasks", classes="section-title")
                    for task in completed_tasks:
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
            self.refresh(recompose=True)

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

        self.refresh(repaint=True, recompose=True, layout=False)

    # Handle task deletion
    @on(t.TaskData.Delete)
    def handle_data_delete(self, data: t.TaskData) -> None:
        """
        Handles deleting a task from the database.

        Args:
            data (t.TaskData): Event data containing the task to delete.
        """
        db = PomodoroDB()
        try:
            db.delete_task(data.task.id)
            print(f"Task with ID {data.task.id} deleted.")
        except Exception as e:
            print(f"Error deleting task: {e}")
