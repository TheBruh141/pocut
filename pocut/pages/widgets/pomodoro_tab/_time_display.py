import copy
from datetime import datetime
from typing import Callable

import pytz
from textual.containers import Vertical, Center
from textual.reactive import reactive, Reactive
from textual.widgets import Static, ProgressBar, Digits, Label

from pocut import AppState
from pocut.state import AppStateChanged
from pocut.utils.session_slice_progressbar import SessionSlicesProgressBar
from pocut.utils.task import SessionSlice


class WorldClock(Static):
    """
    @class WorldClock
    @brief A widget to display the current time in a specified timezone.
    """

    timezone: Reactive[str] = Reactive("Turkey")
    time_display = reactive("")
    detail_level = reactive(1)  # Level of detail: 1 = minimal, 2 = detailed, 3 = full

    def __init__(
        self, state: AppState, timezone: str = "UTC", detail_level: int = 1, **kwargs
    ):
        """
        @brief Initialize the WorldClock with a specific timezone and detail level.
        @param timezone The timezone for the clock (default: "UTC").
        @param detail_level Level of detail to display (1 = minimal, 2 = detailed, 3 = full).
        """
        super().__init__(**kwargs)
        self.timezone = timezone
        self.detail_level = detail_level
        self.set_interval(1, self.update_time)  # Update every second
        self.state = copy.deepcopy(state)

    def on_mount(self) -> None:
        """
        @brief Called when the widget is mounted. Initializes the displayed time.
        """
        self.update_time()

    def update_time(self) -> None:
        """
        @brief Update the displayed time based on the current timezone and detail level.
        also updates the state
        """
        if (
            self.state.config.__str__()
            != AppState(self.state.config_path, self.state.debug_mode).config.__str__()
        ):
            self.post_message(AppStateChanged())
            self.notify(
                f"{AppState(self.state.config_path, self.state.debug_mode).config.__str__()}"
            )
            self.state = AppState(self.state.config_path, self.state.debug_mode)
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

        self.wc = WorldClock(state=state, timezone="UTC", id="utc_clock")

    def set_on_time_up_callback(self, callback):
        """
        @brief Set a callback to be called when time is up.
        @param callback Function to call when the timer completes.
        """
        self.on_time_up_callback = callback

    # noinspection PyTypeChecker
    def on_mount(self) -> None:
        """
        @brief Called when the widget is mounted. Sets up the timer update interval and progress bar.
        """
        self.update_timer = self.set_interval(1, self.update_time, pause=True)
        self.border_title = "Time Remaining"

        # Create and add the ProgressBar widget
        # TODO:
        # self.progress_bar = SessionSlicesProgressBar(
        #     total=self.state.work_duration,
        #     id="time_left_progress_bar",
        # )

        self.progress_bar = ProgressBar(
            total=100,
            show_bar=True,
            show_percentage=True,
            show_eta=False,
        )
        self.time_str: str = self.calculate_time(self.state.work_duration)
        if self.state.clock_type:
            self.digits: Digits = Digits(value=self.time_str, id="timer_digits")
        else:
            self.digits = Label(self.time_str)

        self.mount(
            Vertical(Center(self.digits), Center(self.wc), Center(self.progress_bar))
        )

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
