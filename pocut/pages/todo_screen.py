from datetime import datetime

from textual import on, work, lazy
from textual.app import ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    Vertical,
    ScrollableContainer,
    VerticalScroll,
)
from textual.widgets import (
    Label,
    Button,
    Footer,
)
import pocut.utils.task as t
from pocut import AppState
from pocut.pages.widgets.todo_tab import TaskCreatorModal
from pocut.pages.widgets.todo_tab import TodoTask
from pocut.utils import PomodoroDB

from pocut.pages.widgets.common import SmallButton


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

        # check if it needs to be added or removed from tracking
        if data.task.ongoing == True and not data.task.completed:
            db.add_task_to_tracking(data.task.id)
        elif data.task.ongoing == True and data.task.completed:
            db.remove_tracking_tasks(data.task.id)
        elif not data.task.ongoing:
            db.remove_tracking_tasks(data.task.id)

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
