from textual import on, events, lazy
from textual.app import ComposeResult
from textual.containers import Container, Center, ScrollableContainer
from textual.widgets import Static, Label, Rule

from pocut.pages.widgets.common import SmallButton
from pocut.pages.widgets.todo_tab import TodoTask
from pocut.utils import PomodoroDB, Task
from pocut.utils.task import TaskData
from pocut.utils.taskmanager import ShouldCheckDatabase


class TrackedTask(Static, can_focus=True):

    BINDINGS = [
        ("t", "set_tracked", "untrack task"),
        ("c", "set_completed", "complete task"),
    ]

    def __init__(self, task: Task, **kwargs):
        super().__init__(**kwargs)
        self.info = task

    def compose(self) -> ComposeResult:

        with Container(id="tracked-task-tracker"):

            yield Label(">>>", id="selector")
            yield Label(f"{self.info.id}")
            yield Label(f"{self.info.title}")
            yield Label(f"{self.info.due_date if self.info.due_date else 'N.S'}")
            yield Label(f"{self.info.priority}")

    @on(events.Focus)
    def handle_focus(self):
        self.query_one("#selector", Label).add_class("visible")

    @on(events.Blur)
    def handle_blur(self):
        self.query_one("#selector", Label).remove_class("visible")

    def action_set_tracked(self):
        # noinspection PyTypeChecker
        p: Tracker = self.parent.parent
        p.db.remove_tracking_tasks(self.info.id)
        self.post_message(ShouldCheckDatabase())
        self.notify("untracked task")
        p.check_tasks()

    # noinspection PyTypeChecker
    def action_set_completed(self):
        # noinspectiono PyTypeChecker
        p: Tracker = self.parent.parent
        p.db.set_task_completion_task(self.info)
        p.check_tasks()
        self.notify("complete task")


class Tracker(Static, can_focus=False):
    db: PomodoroDB

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.db = PomodoroDB()
        self.tasks: list[Task] = self.check_tasks()

    def check_tasks(self) -> list[Task]:
        """
        !!!NOTE!!! This function is called when the data is updated. It should be treated like
                   @on(ShouldCheckDatabase)

                   Since Textual does not have a proper way to propagate messages down
                   we are duct tape and hope for this thing to work.


        We are not polling the database, but we are very agressively checking it.
        basically polling with more steps
        """
        # self.notify("updated")
        self.tasks = [Task.from_dict(t) for t in self.db.get_ongoing_tracked_tasks()]
        # self.notify(f"{self.db.get_ongoing_tracked_tasks()}")
        # self.notify(f"{self.tasks}")
        self.refresh(repaint=True, layout=True, recompose=True)
        return self.tasks

    def compose(self) -> ComposeResult:
        # self.notify("updated screen")
        with Center():
            yield Label("# Tasks", id="title")
            yield Rule(id="seperator")

        with lazy.Reveal(ScrollableContainer()):
            for t in self.tasks:
                self.notify(t.__str__())
                yield TrackedTask(t)

    def on_mount(self):
        self.check_tasks()
