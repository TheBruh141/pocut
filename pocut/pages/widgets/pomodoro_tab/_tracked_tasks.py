from textual.widgets import Static

from pocut.utils import PomodoroDB


class TrackedTasks(Static):
    db: PomodoroDB

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.db = PomodoroDB()
