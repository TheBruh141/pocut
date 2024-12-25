import sys

import argparse

from pathlib import Path

# Path to the configuration file
DEFAULT_CONFIG_PATH = Path("pocut_config.toml")
DEFAULT_LOG_FILE = "logs/latest.log"
DEFAULT_MAX_LOG_FILE_SIZE_MB = 5


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="A modern Pomodoro timer application with configurable logging."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging to the console.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=DEFAULT_LOG_FILE,
        help="Specify the log file path. Default: pocut_debug.log",
    )
    parser.add_argument(
        "--max-debug-file-size",
        type=int,
        default=DEFAULT_MAX_LOG_FILE_SIZE_MB,
        help=(
            "Maximum size (in MB) for the debug log file before it rotates. "
            f"Default: {DEFAULT_MAX_LOG_FILE_SIZE_MB} MB."
        ),
    )
    return parser.parse_args()
