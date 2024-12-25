"""
pocut - A Pomodoro timer application.
"""

from .config import parse_args
from .state import AppState
from .utils import audio
from .widgets import *

__version__ = "0.0.1"

# Optional: Define what's accessible when using `from pocut import *`
__all__ = ["parse_args" , "AppState", "audio", "pomodoro_tab", "settings_tab"]
__name__ = "pocut"
