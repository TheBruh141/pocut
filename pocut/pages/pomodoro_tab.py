from functools import cache

from textual import on, events, work
from textual.app import ComposeResult
from textual.containers import Vertical, Center, Horizontal
from textual.widgets import Static, Button, Footer, Label
from pocut.pages.widgets.pomodoro_tab import TimeDisplay, Tracker
from pocut.pages.widgets.pomodoro_tab import PhaseDisplay

from pocut.state import AppState, AppStateChanged
from pocut.utils.audio import (
    initialize_audio,
    set_volume,
    play_sound_time,
)
from pocut.utils.notifications import notify


class PomodoroTab(Static):
    """
    @class PomodoroTab
    @brief A Pomodoro timer widget containing a TimeDisplay, PhaseDisplay, and controls.
    """

    BINDINGS = [
        ("s", "start_timer", "Start/Stop the timer"),
        ("r", "reset_timer", "Reset the timer"),
        ("c", "toggle_phase", "Change phase"),
    ]
    phase_display: PhaseDisplay
    time_display: TimeDisplay

    def __init__(self, config_path, debug_mode) -> None:
        """
        @brief Initialize the PomodoroClock widget.
        @param state Shared application state.
        @param debug_mode Whether debug mode is enabled.
        """
        super().__init__()
        self.recompose_due_to_tracker = False
        self.tracker = None
        self.state = AppState(config_path, debug_mode)

    def on_mount(self) -> None:
        """
        @brief Called when the widget is mounted. Initializes the timer display without starting it.
        """
        self.time_display = self.query_one(TimeDisplay)
        self.time_display.set_on_time_up_callback(self.on_time_up)
        self.phase_display = self.query_one(PhaseDisplay)  # Get the PhaseDisplay widget
        self.update_timer_for_current_phase()
        # Initialize the audio system
        initialize_audio()
        set_volume(1)

    def on_time_up(self) -> None:
        """
        @brief Switch to the next phase when the timer completes.
        """
        notify(
            "Pomodoro Timer Up!",
            f"congratulations on staying focused for {self.state.work_duration}",
        )
        # Play the configured finish sound
        finish_sound = self.state.finish_sound
        play_sound_time(finish_sound, 10, True, 5)
        if self.state.debug_mode:
            self.app.notify(f"Should have played {finish_sound}")
        # Switch phases and update the timer
        phase = self.state.toggle_phase()
        self.update_timer_for_current_phase()

        # Update UI
        self.phase_display.update_phase()  # Update the phase display
        start_stop_button = self.query_one("#start_stop")
        start_stop_button.label = "Start"
        start_stop_button.variant = "success"
        self.app.notify(f"Switched to {phase} phase!")

    def update_timer_for_current_phase(self) -> None:
        """
        @brief Set the timer display to the current phase's duration without starting it.
        """
        duration = (
            self.state.work_duration
            if self.state.is_work_phase
            else self.state.break_duration
        )
        self.time_display.reset()  # Ensure the timer is stopped
        self.time_display.duration = duration
        self.time_display.remaining_time = duration
        if self.time_display.digits:
            self.time_display.digits.update(
                self.time_display.calculate_time(duration)
            )  # Update digits
        self.time_display.update_progress_bar()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        @brief Handle button press events.
        @param event Button press event.
        """
        button_id = event.button.id

        if button_id == "start_stop":
            if self.time_display.timer_active:
                self.time_display.stop()
                event.button.label = "Continue"
                event.button.variant = "success"
            elif self.time_display.paused:
                self.time_display.start()
                event.button.label = "Stop"
                event.button.variant = "error"
            else:
                self.time_display.start()
                event.button.label = "Stop"
                event.button.variant = "error"
        elif button_id == "reset":
            self.time_display.reset()
            self.update_timer_for_current_phase()
            start_stop_button = self.query_one("#start_stop")
            start_stop_button.label = "Start"
            start_stop_button.variant = "success"
        elif button_id == "toggle_phase":
            phase = self.state.toggle_phase()
            self.update_timer_for_current_phase()
            self.phase_display.update_phase()  # Update phase display
            start_stop_button = self.query_one("#start_stop")
            start_stop_button.label = "Start"
            start_stop_button.variant = "success"
            self.app.notify(f"Switched to {phase} phase!")

    # @cache
    @on(AppStateChanged)
    def handle_state_changed(self) -> None:
        self.state = AppState(
            config_path=self.state.config_path, debug_mode=self.state.debug_mode
        )
        self.query_one("#reset", Button).press()
        # self.refresh(repaint=True, layout=True, recompose=True)

    def compose(self) -> ComposeResult:
        """:
        @brief Compose the layout of the Pomodoro widget.
        @return ComposeResult containing the widget layout.
        """
        with Vertical():
            with Center(id="clock_cluster"):
                yield TimeDisplay(id="main_clock", state=self.state)

                with Center():
                    yield PhaseDisplay(self.state, id="phase_show")

                with Center():
                    self.tracker = Tracker(id="tracked_tasks")
                    yield self.tracker

            with Horizontal(id="button_cluster"):
                yield Button("Start", id="start_stop", variant="success")
                yield Button("Reset", id="reset")
                yield Button("Toggle Phase", id="toggle_phase", variant="primary")
        yield Footer()

    def update_tracker(self):
        # self.notify("should update tracker")
        self.tracker.check_tasks()
        self.recompose_due_to_tracker = True

    @on(events.Show)
    async def handle_update(self) -> None:
        if self.recompose_due_to_tracker:
            await self.tracker.recompose()
            self.recompose_due_to_tracker = False

            # self.notify("should handle focus")

    def action_start_timer(self):
        button = self.query_one("#start_stop", Button)
        button.post_message(Button.Pressed(button))

    def action_reset_timer(self):
        button = self.query_one("#reset", Button)
        button.post_message(Button.Pressed(button))

    def action_toggle_phase(self):
        button = self.query_one("#toggle_phase", Button)
        button.post_message(Button.Pressed(button))
