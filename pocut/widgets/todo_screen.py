from datetime import datetime
from dataclasses import asdict
from textual.app import ComposeResult
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import DataTable, Input, Button, Static, Label, Select, Collapsible
from textual.containers import Vertical, Center, Horizontal
from textual.app import App

from pocut import AppState
from pocut.utils.taskmanager import Task, TaskManager  # Assume Task and TaskManager are implemented as discussed


class TaskCreatorWidget(Vertical):
    """
    Widget for creating a new task.
    """
    INTERVAL_OPTIONS = [
        "No Interval",
        "Daily",
        "Weekly",
        "Monthly",
        "Yearly",
    ]

    def __init__(self, task_manager: TaskManager, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = task_manager

    def compose(self) -> ComposeResult:
        """
        Compose the layout for the widget.
        """
        with Vertical(id="task_form"):
            yield Label("Create a New Task", id="modal_title")

            yield Label("Task Title")
            yield Input(placeholder="Enter task title", id="task_title_input")

            yield Label("Task Description")
            yield Input(placeholder="Enter task description", id="task_description_input")

            with Collapsible(title="Advanced Settings"):
                yield Label("Priority (1-5)")
                yield Input(placeholder="1 (lowest) to 5 (highest)", id="priority_input")

                yield Label("Due Date (YYYY-MM-DD)")
                yield Input(placeholder="Enter due date", id="due_date_input")

                yield Label("Interval")
                yield Select(
                    [(interval, index) for index, interval in enumerate(self.INTERVAL_OPTIONS)],
                    id="interval_selector",
                )

            with Center():
                yield Button("Create Task", id="create_task_button", variant="success")

            yield Label("", id="status_label")

    async def on_button_pressed(self, event: Button.Pressed):
        """
        Handle button presses.
        """
        if event.button.id == "create_task_button":
            await self.create_task()

    async def create_task(self):
        """
        Validate inputs and create a new task using the TaskManager.
        """
        # Fetch input values
        title = self.query_one("#task_title_input", Input).value.strip()
        description = self.query_one("#task_description_input", Input).value.strip()
        priority = self.query_one("#priority_input", Input).value.strip()
        due_date = self.query_one("#due_date_input", Input).value.strip()
        interval_index = self.query_one("#interval_selector", Select).value

        # Input validation
        if not title:
            self.query_one("#status_label", Label).update("Task title is required.")
            return

        if not description:
            self.query_one("#status_label", Label).update("Task description is required.")
            return

        try:
            priority = int(priority)
            if priority < 1 or priority > 5:
                raise ValueError
        except ValueError:
            self.query_one("#status_label", Label).update("Priority must be an integer between 1 and 5.")
            return

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                self.query_one("#status_label", Label).update("Due date must be in YYYY-MM-DD format.")
                return

        # Determine interval settings
        interval_options = {
            1: {"is_daily": True},
            2: {"is_weekly": True},
            3: {"is_monthly": True},
            4: {"is_yearly": True},
        }
        interval_settings = interval_options.get(interval_index, {})

        # Create task object
        task = Task(
            title=title,
            text=description,
            priority=priority,
            due_date=due_date if due_date else None,
            **interval_settings
        )

        # Save task to the database
        try:
            self.task_manager.add_task(task)
            self.query_one("#status_label", Label).update("Task created successfully!")
        except Exception as e:
            self.query_one("#status_label", Label).update(f"Error creating task: {e}")


class TaskCreatorModal(ModalScreen):
    """
    Modal screen for task creation.
    """

    def __init__(self, task_manager: TaskManager, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = task_manager

    def compose(self) -> ComposeResult:
        """
        Compose the layout for the modal screen.
        """
        yield TaskCreatorWidget(self.task_manager)

    def on_key(self, event: Key):
        if event.key == "escape":
            self.dismiss()


class TodoTab(Vertical):
    """
    Tab for managing tasks.
    """

    def __init__(self, state: AppState, **kwargs):
        super().__init__(**kwargs)
        self.state = state
        self.task_manager = TaskManager(state.database_path)

    def compose(self) -> ComposeResult:
        """
        Compose the To-Do tab layout.
        """
        with Vertical():
            yield Center(Label("To-Do List"))

            with Vertical(id="task_list"):
                tasks = self.task_manager.get_all_tasks()
                for task in tasks:
                    yield Static(f"{task.title}: {task.text}")

            yield Button("Create New Task", id="open_task_creator_button", variant="primary")

    async def on_button_pressed(self, event: Button.Pressed):
        """
        Handle button presses.
        """
        if event.button.id == "open_task_creator_button":
            self.app.push_screen(TaskCreatorModal(self.task_manager))
