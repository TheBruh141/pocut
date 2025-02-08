import asyncio
from datetime import datetime
from typing import Any

from textual import on, work, lazy
from textual.app import ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    Vertical,
    ScrollableContainer,
    VerticalScroll,
)
from textual.events import Event
from textual.message_pump import Callback
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
from pocut.utils.taskmanager import ShouldCheckDatabase


class TodoTab(Container):
    BINDINGS = [
        ("a", "create_task", "create task"),
        # ("d", "delete_task", "delete task"), #TODO
        # ("e", "edit_task", "edit task"),
    ]
    db: PomodoroDB

    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        self.db = PomodoroDB()
        self.task_widgets: list[TodoTask] = []

    def on_mount(self):

        for w in self.children:
            w.border_title = f"{w.id if w.id else "NO COMNKING NAME"}"

        self.recompose()

    def compose(self) -> ComposeResult:
        self.task_widgets = []  # flush
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

                if len(uncompleted_tasks) >= 128:
                    slot = lazy.Reveal(VerticalScroll(id="uncompleted-tasks-section"))
                else:
                    slot = VerticalScroll(id="uncompleted-tasks-section")

                slot.border_title = f"TASKS ({len(uncompleted_tasks)})"
                """
                if the tasks size is bigger than 128 due to memory constrains,
                we are opting to wait a lil more for lazy loading.
                """
                with slot:
                    for task in uncompleted_tasks:
                        task_widget = TodoTask(task)
                        self.task_widgets.append(task_widget)
                        yield task_widget

            # Render completed tasks
            if completed_tasks:
                """
                same here
                """
                if len(completed_tasks) >= 128:
                    slot = lazy.Reveal(Vertical(id="completed-tasks-section"))
                else:
                    slot = VerticalScroll(id="completed-tasks-section")
                slot.border_title = f"COMPLETED ({len(completed_tasks)})"
                with slot:
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
            self.persistent_refresh(recompose=True)

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
            self.post_message(ShouldCheckDatabase())
            print(f"Task created with ID: {task_id}")
        except Exception as e:
            print(f"Error creating task: {e}")

    def persistent_refresh(
        self, repaint: bool = False, layout: bool = False, recompose: bool = False
    ) -> None:
        self.notify("Refreshing...")
        self.refresh(repaint=repaint, layout=layout, recompose=recompose)

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
            self.post_message(ShouldCheckDatabase())
            print(f"Task with ID {data.task.id} updated.")
        except Exception as e:
            print(f"Error updating task: {e}")

        self.persistent_refresh(repaint=True, recompose=True, layout=False)

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
            self.post_message(ShouldCheckDatabase())
            print(f"Task with ID {data.task.id} deleted.")
        except Exception as e:
            print(f"Error deleting task: {e}")

    @on(t.TaskData.Complete)
    def handle_data_complete(self, data: t.TaskData) -> None:
        """
        Handles Completing an existing task in the database.
        """
        self.notify("Completing task...")
        db = PomodoroDB()
        try:
            db.set_task_completion_task(data.task)
            self.post_message(ShouldCheckDatabase())
            print(f"Task with ID {data.task.id} updated.")
            self.persistent_refresh(recompose=True, layout=True)
        except Exception as e:
            print(f"Error updating task: {e}")

    def action_create_task(self):
        # why reinvent the wheel when you can steal it from your
        # "__class mates__"
        # yep. I'll see my self out...
        self.on_button_pressed(Button.Pressed(Button(id="add-task")))
        # self.notify("pressed a")

    def update_self(self):
        """
        This function is called specifically when an update to the database had been made
        and we are aware of it. This allows it so that we don't have any data continuity issues.

        :return:
        """
        self.persistent_refresh(recompose=True, layout=True)
        pass
