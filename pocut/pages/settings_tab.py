from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Container, Center, Horizontal
from textual.widgets import Button, Input, Label, Footer, Switch

from pocut.state import AppState
from pocut.pages.widgets.common import FileSelectorModal


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
            with Vertical(id="misc") as v:
                v.border_title = "Misc"
                with Horizontal():
                    clock_type = self.state.config["misc"]["clock_type"]
                    yield Switch(value=clock_type, id="misc_clock_type_selector")
                    with Vertical():
                        yield Label("Clock Type")
                        yield Label(
                            f"> Current type: {"big" if clock_type is True else "small"}",
                            id="misc_clock_type_selector_indicator",
                        )

            with Center() as c:
                yield Button("Save", id="save_settings_button", variant="success")

            yield Footer()

    @on(Switch.Changed, "#misc_clock_type_selector")
    def change_clock_type(self):
        self.state.config["misc"]["clock_type"] = not self.state.config["misc"][
            "clock_type"
        ]
        self.state.save_config(self.state.config)
        self.notify(
            f"> Current type:"
            f" {"big" if self.state.config["misc"]["clock_type"] is True else "small"}\n"
            f"this action requires restarting to take effects",
            severity="information",
        )

        self.query_one("#misc_clock_type_selector_indicator", Label).update(
            f"> Current type: {"big" if self.state.config["misc"]["clock_type"] is True else "small"}"
        )

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
            self.notify("saved!")
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

        self.state.save_config(self.state.config)
