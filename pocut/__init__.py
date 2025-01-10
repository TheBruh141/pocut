"""
pocut - A Pomodoro timer application.
"""

from .config import parse_args
from .state import AppState
from .utils import audio
from .pages import TodoTab, SettingsTab, PomodoroTab

__version__ = "0.0.1"

__name__ = "pocut"
