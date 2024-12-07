import sys

from loguru import logger
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


def configure_logging(debug: bool, log_file: str, max_file_size_mb: int):
    """
    Configure logging using loguru.

    Args:
        debug (bool): Whether to enable verbose logging to the console.
        log_file (str): Path to the log file.
        max_file_size_mb (int): Maximum log file size in megabytes before rotating.
    """
    logger.remove()  # Remove default logger

    # Set logging format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Add console logger
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if debug else "INFO",
        colorize=True,
    )

    # Add file logger with rotation
    max_file_size_bytes = max_file_size_mb * 1024 * 1024  # Convert MB to bytes
    logger.add(
        log_file,
        format=log_format,
        level="DEBUG",
        rotation=max_file_size_bytes,
        retention="10 days",  # Optional: keep logs for 10 days
        compression="zip",  # Compress old log files
    )

    logger.debug(f"Logging configured. Debug mode: {debug}, Log file: {log_file}")
