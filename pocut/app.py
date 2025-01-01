from textual import on
from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, Tabs, Button

from pocut import AppState
from pocut.config import DEFAULT_CONFIG_PATH, parse_args
from pocut.widgets import PomodoroClock, SettingsTab
from pocut.widgets.todo_screen import TodoTab


class PocutApp(App):
    """
    Main application class for the Pomodoro timer.

    Attributes:
        CSS_PATH (str): Path to the application's CSS file.
        BINDINGS (list): Key bindings for the application.
        state (AppState): The shared application state.
    """

    CSS_PATH = "pocut.tcss"
    BINDINGS = [
        ("s", "start_timer", "Start/Stop the timer"),
        ("r", "reset_timer", "Reset the timer"),
        ("c", "toggle_phase", "Change phase"),
    ]

    # BINDINGS = [
    #     ("a", "previous_tab", "Switch to the previous tab"),
    #     ("d", "next_tab", "Switch to the next tab"),
    # ]
    _tabs: TabbedContent

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
        with TabbedContent(id="the-parent") as tc:
            self._tabs = tc
            with TabPane("Pomodoro", id="pomodoro"):
                yield PomodoroClock(self.state.config_path, self.state.debug_mode)
            with TabPane("Todos"):
                yield TodoTab(self.state)

            with TabPane("Settings", id="settings"):
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

    def action_start_timer(self):
        button = self.query_one("#start_stop", Button)
        button.post_message(Button.Pressed(button))

    def action_reset_timer(self):
        button = self.query_one("#reset", Button)
        button.post_message(Button.Pressed(button))

    def action_toggle_phase(self):
        button = self.query_one("#toggle_phase", Button)
        button.post_message(Button.Pressed(button))

    # def action_next_tab(self) -> None:
    #     """
    #     Switch to the next tab in the TabbedContent.
    #     """
    #
    #     tabs = self.query_one(Tabs)
    #     tabs.action_next_tab()
    #
    # def action_previous_tab(self) -> None:
    #     """
    #     Switch to the previous tab in the TabbedContent.
    #     """
    #     self.notify("Previous Tab")
    #     self._tabs.action_previous_tab()
