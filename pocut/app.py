from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane

from loguru import logger

from pocut import AppState
from pocut.config import DEFAULT_CONFIG_PATH, parse_args, configure_logging
from pocut.widgets import PomodoroClock, SettingsTab
from pocut.widgets.todo_screen import TodoTab


# from pocut.widgets.todo_screen import TodoTab


class PocutApp(App):
    """
    Main application class for the Pomodoro timer.

    Attributes:
        CSS_PATH (str): Path to the application's CSS file.
        BINDINGS (list): Key bindings for the application.
        state (AppState): The shared application state.
    """
    CSS_PATH = "pocut.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self, debug: bool):
        """
        Initialize the application.

        Args:
            debug (bool): Whether debug mode is enabled.
        """
        super().__init__()
        self.state = AppState(DEFAULT_CONFIG_PATH, debug_mode=debug)

    def compose(self) -> ComposeResult:
        """
        Compose the app layout.

        Returns:
            ComposeResult: The app layout.
        """
        with TabbedContent(id="the-parent"):
            with TabPane("Pomodoro"):
                yield PomodoroClock(self.state)
            with TabPane("Todos"):
                yield TodoTab(self.state)

            with TabPane("Settings"):
                yield SettingsTab(self.state)

    def action_set_durations(self, work: int, break_: int) -> None:
        """
        Set the durations for work and break phases.

        Args:
            work (int): Work phase duration in seconds.
            break_ (int): Break phase duration in seconds.
        """
        self.state.work_duration = work
        self.state.break_duration = break_
        logger.info(f"Durations updated: Work={work} seconds, Break={break_} seconds.")

    def action_toggle_dark(self) -> None:
        """
        Toggle between dark and light modes.
        """
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"


