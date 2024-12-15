"""
pocut - A Pomodoro timer application.
"""

from .config import parse_args, configure_logging
from .state import AppState
from .utils import audio
from .widgets import pomodoro_clock, settings_tab

__version__ = "0.0.1"

# Optional: Define what's accessible when using `from pocut import *`
__all__ = ["parse_args", "configure_logging", "AppState", "audio", "pomodoro_clock", "settings_tab"]
__name__ = "pocut"
