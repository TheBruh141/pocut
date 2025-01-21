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
        "--dump-dom",
        metavar="FILE",
        nargs="?",
        const="dom.textual_dom_dump",  # Default filename if no argument is provided
        help="Dump DOM configuration to a file. Default: 'dom.textual_dom_dump'.",
    )
    return parser.parse_args()
