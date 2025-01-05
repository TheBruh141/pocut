from datetime import datetime
from functools import cache

import pytz
from rich.align import VerticalCenter
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Center, Horizontal
from textual.events import Event
from textual.reactive import reactive, Reactive
from textual.widgets import Static, Button, Footer, ProgressBar, Label, Digits

from pocut.state import AppState

from pocut.utils.audio import initialize_audio, set_volume, play_sound_blocking
from pocut.widgets.common.custom_button import SmallButton


class WorldClock(Static):
    """
    @class WorldClock
    @brief A widget to display the current time in a specified timezone.
    """

    timezone: Reactive[str] = Reactive("Turkey")
    time_display = reactive("")
    detail_level = reactive(1)  # Level of detail: 1 = minimal, 2 = detailed, 3 = full

    def __init__(self, timezone: str = "UTC", detail_level: int = 1, **kwargs):
        """
        @brief Initialize the WorldClock with a specific timezone and detail level.
        @param timezone The timezone for the clock (default: "UTC").
        @param detail_level Level of detail to display (1 = minimal, 2 = detailed, 3 = full).
        """
        super().__init__(**kwargs)
        self.timezone = timezone
        self.detail_level = detail_level
        self.set_interval(1, self.update_time)  # Update every second

    def on_mount(self) -> None:
        """
        @brief Called when the widget is mounted. Initializes the displayed time.
        """
        self.update_time()

    def update_time(self) -> None:
        """
        @brief Update the displayed time based on the current timezone and detail level.
        """
        # tz = pytz.timezone(self.timezone)
        tz = pytz.timezone("Turkey")
        now = datetime.now(tz)

        if self.detail_level == 1:  # Minimal: Only time
            current_time = now.strftime("%H:%M:%S")
            self.update(f"{current_time}")
        elif self.detail_level == 2:  # Detailed: Time and date
            current_time = now.strftime("%H:%M:%S\n%Y-%m-%d")
            self.update(f"Time: {current_time}")
        elif self.detail_level == 3:  # Full: Time, date, and timezone
            current_time = now.strftime("%H:%M:%S\n%Y-%m-%d")
            self.update(f"Timezone: {self.timezone}\n{current_time}")

    def set_detail_level(self, level: int) -> None:
        """
        @brief Set the detail level and update the display.
        @param level The desired detail level (1, 2, or 3).
        """
        if level in [1, 2, 3]:
            self.detail_level = level
            self.update_time()  # Immediately reflect changes


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

    def __init__(self, state: AppState, *args, **kwargs):
        """
        @brief Initialize TimeDisplay with an optional event callback.
        """
        super().__init__(*args, **kwargs)
        self.time_str = None
        self.state = state
        # self.notify(f"{self.time_str=}, {self.state.work_duration}")
        self.digits = None
        self.update_timer = None
        self.on_time_up_callback = None
        self.progress_bar = None  # ProgressBar instance
        self.wc = WorldClock(timezone="UTC", id="utc_clock")

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
        self.time_str: str = self.calculate_time(self.state.work_duration)
        if self.state.clock_type:
            self.digits: Digits = Digits(value=self.time_str, id="timer_digits")
        else:
            self.digits = Label(self.time_str)

        self.mount(Vertical(Center(self.digits), Center(self.wc), self.progress_bar))

        self.update_progress_bar()

        # initialize the time for the cold start
        self.reset()

    def update_time(self) -> None:
        """
        @brief Decrement the remaining time by one second. Stop the timer if it reaches zero.
        """
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_progress_bar()
            self.digits.update(self.time_str)
        else:
            self.stop()
            if self.on_time_up_callback:
                self.on_time_up_callback()

    # def start(self, duration: int = None) -> None:
    #     """
    #     @brief Start or resume the countdown.
    #     @param duration (Optional) Initial duration for the countdown.
    #     """
    #     if duration is not None:
    #         self.duration = duration
    #         self.remaining_time = duration
    #     self.timer_active = True
    #     self.paused = False
    #     self.update_timer.resume()
    #     self.update_progress_bar()  # Update progress bar immediately
    def start(self, duration: int = None) -> None:
        """
        @brief Start or resume the countdown.
        @param duration (Optional) Initial duration for the countdown.
        """
        if duration is not None:
            self.duration = duration
            self.remaining_time = duration
            if self.digits:
                self.digits.update(
                    self.calculate_time(self.remaining_time)
                )  # Update digits
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
        if self.digits:
            self.digits.update(
                self.calculate_time(self.remaining_time)
            )  # Update digits
        self.paused = False
        self.update_progress_bar()  # Reset progress bar

    @staticmethod
    def calculate_time(remaining_time: float) -> str:
        minutes, seconds = divmod(remaining_time, 60)
        return f"{int(minutes):02}:{int(seconds):02}"

    def watch_remaining_time(self, remaining_time: float) -> None:
        """
        @brief Update the displayed time whenever the remaining time changes.
        @param remaining_time Current remaining time in seconds.
        """
        minutes, seconds = divmod(remaining_time, 60)
        self.time_str = f"{int(minutes):02}:{int(seconds):02}"
        if self.digits:
            self.digits.update(
                self.time_str
            )  # Ensure Digits widget syncs with remaining_time
        self.update()

    def update_progress_bar(self) -> None:
        """
        @brief Update the progress bar based on the remaining time.
        """
        if self.progress_bar and self.duration > 0:
            progress = (self.remaining_time / self.duration) * 100
            self.progress_bar.progress = int(progress)


class PomodoroClock(Static):
    """
    @class PomodoroClock
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
        """
        super().__init__()
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

    @cache
    def compose(self) -> ComposeResult:
        """
        @brief Compose the layout of the Pomodoro widget.
        @return ComposeResult containing the widget layout.
        """
        with Vertical():
            with Center(id="clock_cluster"):
                yield TimeDisplay(id="main_clock", state=self.state)

                with Center():
                    yield PhaseDisplay(
                        self.state, id="phase_show"
                    )  # Add PhaseDisplay widget
            with Center(id="button_cluster"):
                yield Button("Start", id="start_stop", variant="success")
                yield Button("Reset", id="reset")
                yield Button("Toggle Phase", id="toggle_phase", variant="primary")
        yield Footer()

    def action_start_timer(self):
        button = self.query_one("#start_stop", Button)
        button.post_message(Button.Pressed(button))

    def action_reset_timer(self):
        button = self.query_one("#reset", Button)
        button.post_message(Button.Pressed(button))

    def action_toggle_phase(self):
        button = self.query_one("#toggle_phase", Button)
        button.post_message(Button.Pressed(button))
