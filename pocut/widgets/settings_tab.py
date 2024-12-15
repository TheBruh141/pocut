from textual.app import ComposeResult
from textual.widgets import Button, Input, Label, Checkbox
from textual.containers import Vertical, Container, Center
from pocut.state import AppState
from pocut.widgets.filemodal import FileSelectorModal


class SettingsTab(Container):
    """
    A tab for adjusting Pomodoro settings.
    """

    def __init__(self, state: AppState):
        super().__init__(id="settings_tab")
        self.state = state

    def compose(self) -> ComposeResult:
        """
        Compose the settings tab layout.
        """
        # Fetch the current configuration values from the state
        current_sound_path = self.state.finish_sound
        work_duration = self.state.work_duration // 60  # Convert to minutes
        break_duration = self.state.break_duration // 60  # Convert to minutes

        with Vertical(id="settings_container"):
            # Sound Settings
            with Vertical(id="sound_settings") as v:
                v.border_title = "Sound Settings"
                yield Input(
                    value=current_sound_path,
                    placeholder="Enter sound file path",
                    id="sound_file_input",
                )
                yield Button("Browse", id="browse_sound_button", variant="primary")

            # Time Settings
            with Vertical(id="time_settings") as v:
                v.border_title = "Time Settings"
                yield Label("Work Time")
                yield Input(
                    value=str(work_duration),
                    placeholder="Work duration (minutes)",
                    id="work_duration_input",
                )
                yield Label("Break Time")
                yield Input(
                    value=str(break_duration),
                    placeholder="Break duration (minutes)",
                    id="break_duration_input",
                )

            # Dark Mode and Save Button
            with Vertical(id="mode_selector"):
                yield Checkbox("Enable Dark Mode", id="dark_mode_toggle")

            with Center() as c:
                yield Button("Save", id="save_settings_button", variant="success")

    async def on_button_pressed(self, event: Button.Pressed):
        """
        Handle button press events.
        """
        if event.button.id == "browse_sound_button":
            modal = FileSelectorModal(".", supported_extensions={".mp3", ".wav"})
            result = await self.app.push_screen(modal)
            if result:
                self.query_one("#sound_file_input").value = result
                # Update the state with the new file path
                self.state.finish_sound = result
        elif event.button.id == "save_settings_button":
            self.validate_and_save()

    def validate_and_save(self):
        """
        Validate and save the settings.
        """
        # Fetch the input values
        work_duration_input = self.query_one("#work_duration_input", Input).value
        break_duration_input = self.query_one("#break_duration_input", Input).value

        # Validate and update durations
        try:
            work_duration = int(work_duration_input) * 60  # Convert to seconds
            break_duration = int(break_duration_input) * 60  # Convert to seconds

            if work_duration > 0:
                self.state.work_duration = work_duration
            if break_duration > 0:
                self.state.break_duration = break_duration
        except ValueError:
            pass  # Handle invalid inputs gracefully

        # Save other settings (e.g., dark mode, sound file path)
        dark_mode_toggle = self.query_one("#dark_mode_toggle", Checkbox).value
        self.state.config["dark_mode"] = dark_mode_toggle
        self.state.save_config(self.state.config)
