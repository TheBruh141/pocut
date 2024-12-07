from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import (Static,
                             Button, Label, Input)

from pocut.state import AppState


class SettingsTab(Static):
    """
    @class SettingsTab
    @brief A tab for adjusting Pomodoro settings.
    """

    def __init__(self, state: AppState):
        super().__init__()
        self.break_input = None
        self.save_button = None
        self.work_input = None
        self.state = state

    def on_mount(self) -> None:
        """
        @brief Called when the Settings tab is mounted.
        """
        self.work_input = self.query_one("#work_duration_input")
        self.break_input = self.query_one("#break_duration_input")
        self.save_button = self.query_one("#save_settings_button")

        # Set current durations in the inputs
        self.work_input.value = str(self.state.work_duration // 60)  # Convert seconds to minutes
        self.break_input.value = str(self.state.break_duration // 60)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        @brief Handle button press events.
        """
        if event.button.id == "save_settings_button":
            try:
                # Get values from inputs
                work_duration = int(self.work_input.value) * 60
                break_duration = int(self.break_input.value) * 60

                # Update state and notify user
                self.state.work_duration = work_duration
                self.state.break_duration = break_duration
                self.app.notify("Settings saved successfully!")
            except ValueError:
                self.app.notify("Invalid input. Please enter valid numbers.")

    def compose(self) -> ComposeResult:
        """
        @brief Compose the layout for the Settings tab.
        """
        with Vertical():
            yield Label("Settings", id="settings_label", variant="header")
            yield Input(id="work_duration_input", placeholder="Work Duration (minutes)")
            yield Input(id="break_duration_input", placeholder="Break Duration (minutes)")
            yield Button("Save Settings", id="save_settings_button", variant="success")
