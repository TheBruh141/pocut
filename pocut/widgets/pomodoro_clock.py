from textual.app import ComposeResult
from textual.containers import Vertical, Center
from textual.reactive import reactive
from textual.widgets import (Static, Button, Footer,
                             ProgressBar, Label)

from pocut.state import AppState
from loguru import logger

from pocut.utils.audio import initialize_audio, set_volume, play_sound_blocking


class PhaseDisplay(Label):
    """
    @class PhaseDisplay
    @brief A widget to display the current phase (Work or Break).
    """

    def __init__(self, state: AppState, *args, **kwargs):
        """
        @brief Initialize the PhaseDisplay widget with the application state.
        @param state The shared application state to fetch the current phase.
        """
        super().__init__(*args, **kwargs)
        self.state = state
        self.update_phase()  # update the phase so that we have a correct initialization

    def update_phase(self):
        """
        @brief Update the label to show the current phase (Work or Break).
        """
        phase = "Work" if self.state.is_work_phase else "Break"
        self.update(f"Current Phase: {phase}")


class TimeDisplay(Static):
    """
    @class TimeDisplay
    @brief A widget for displaying and managing countdown timers with a progress bar.
    """
    duration = reactive(0.0)
    remaining_time = reactive(0.0)
    timer_active = reactive(False)
    paused = reactive(False)

    def __init__(self, *args, **kwargs):
        """
        @brief Initialize TimeDisplay with an optional event callback.
        """
        super().__init__(*args, **kwargs)
        self.update_timer = None
        self.on_time_up_callback = None
        self.progress_bar = None  # ProgressBar instance

    def set_on_time_up_callback(self, callback):
        """
        @brief Set a callback to be called when time is up.
        @param callback Function to call when the timer completes.
        """
        self.on_time_up_callback = callback

    def on_mount(self) -> None:
        """
        @brief Called when the widget is mounted. Sets up the timer update interval and progress bar.
        """
        self.update_timer = self.set_interval(1, self.update_time, pause=True)
        self.border_title = "Time Remaining"

        # Create and add the ProgressBar widget
        self.progress_bar = ProgressBar(
            total=100,
            id="time_left_progress_bar",
            show_eta=False,
        )

        self.mount(self.progress_bar)

    def update_time(self) -> None:
        """
        @brief Decrement the remaining time by one second. Stop the timer if it reaches zero.
        """
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_progress_bar()
        else:
            self.stop()
            if self.on_time_up_callback:
                logger.debug("Calling on_time_up callback")
                self.on_time_up_callback()

    def start(self, duration: int = None) -> None:
        """
        @brief Start or resume the countdown.
        @param duration (Optional) Initial duration for the countdown.
        """
        if duration is not None:
            self.duration = duration
            self.remaining_time = duration
        self.timer_active = True
        self.paused = False
        self.update_timer.resume()
        self.update_progress_bar()  # Update progress bar immediately

    def stop(self) -> None:
        """
        @brief Pause the countdown.
        """
        self.update_timer.pause()
        self.timer_active = False
        self.paused = True

    def reset(self) -> None:
        """
        @brief Reset the countdown to its initial duration.
        """
        self.stop()
        self.remaining_time = self.duration
        self.paused = False
        self.update_progress_bar()  # Reset progress bar

    def watch_remaining_time(self, remaining_time: float) -> None:
        """
        @brief Update the displayed time whenever the remaining time changes.
        @param remaining_time Current remaining time in seconds.
        """
        minutes, seconds = divmod(remaining_time, 60)
        self.update(f"{int(minutes):02}:{int(seconds):02}")

    def update_progress_bar(self) -> None:
        """
        @brief Update the progress bar based on the remaining time.
        """
        if self.progress_bar and self.duration > 0:
            progress = ((self.remaining_time / self.duration) * 100)
            self.progress_bar.progress = int(progress)


class PomodoroClock(Static):
    """
    @class PomodoroClock
    @brief A Pomodoro timer widget containing a TimeDisplay, PhaseDisplay, and controls.
    """

    def __init__(self, state: AppState) -> None:
        """
        @brief Initialize the PomodoroClock widget.
        @param state Shared application state.
        """
        super().__init__()
        self.phase_display = None
        self.time_display = None
        self.state = state

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
        logger.info("Time is up! Switching to the next phase.")
        # Play the configured finish sound
        finish_sound = self.state.finish_sound
        play_sound_blocking(finish_sound)
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
            self.state.work_duration if self.state.is_work_phase else self.state.break_duration
        )
        self.time_display.reset()  # Ensure the timer is stopped
        self.time_display.duration = duration
        self.time_display.remaining_time = duration

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

    def compose(self) -> ComposeResult:
        """
        @brief Compose the layout of the Pomodoro widget.
        @return ComposeResult containing the widget layout.
        """
        with Vertical():
            with Center(id="clock_cluster"):
                yield TimeDisplay(id="main_clock")
                with Center():
                    yield PhaseDisplay(self.state, id="phase_show")  # Add PhaseDisplay widget
            with Center():
                yield Button("Start", id="start_stop", variant="success")
                yield Button("Reset", id="reset")
                yield Button("Toggle Phase", id="toggle_phase", variant="primary")
        yield Footer()
