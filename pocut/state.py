from pathlib import Path
import toml
from loguru import logger


class AppState:
    """
    Manages the application state and configurations.

    Args:
        config_path (Path): Path to the configuration file.
    """

    def __init__(self, config_path: Path | str, debug_mode: bool):
        self.config_path = config_path
        self.config = self.load_config()
        self.is_work_phase = True
        self.debug_mode: bool = debug_mode

    def load_config(self) -> dict:
        """
        Load configuration from a TOML file or use default values.

        Returns:
            dict: Configuration data.
        """
        if self.config_path.exists():
            logger.debug(f"Loading configuration from {self.config_path}")
            return toml.load(self.config_path)
        else:
            logger.warning(f"Configuration file not found. Using default values.")
            default_config = {
                "durations": {"work_duration": 1500, "break_duration": 300},
                "audio": {
                    "finish_sound": "sounds/default_finish.wav",
                    "start_sound": "sounds/default_start.wav",
                    "stop_sound": "sounds/default_stop.wav",
                },
                "todo": {
                    "database_file_path": "pocut/db/todo.sqlite"
                }
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, config: dict) -> None:
        """
        Save the current configuration to the TOML file.

        Args:
            config (dict): Configuration data.
        """
        logger.info(f"Saving configuration to {self.config_path}")
        with open(self.config_path, "w") as f:
            toml.dump(config, f)

    @property
    def work_duration(self) -> int:
        """
        Retrieve the work duration.

        Returns:
            int: Work duration in seconds.
        """
        return self.config["durations"]["work_duration"]

    @work_duration.setter
    def work_duration(self, value: int) -> None:
        """
        Set the work duration.

        Args:
            value (int): New work duration in seconds.
        """
        self.config["durations"]["work_duration"] = value
        self.save_config(self.config)

    @property
    def break_duration(self) -> int:
        """
        Retrieve the break duration.

        Returns:
            int: Break duration in seconds.
        """
        return self.config["durations"]["break_duration"]

    @break_duration.setter
    def break_duration(self, value: int) -> None:
        """
        Set the break duration.

        Args:
            value (int): New break duration in seconds.
        """
        self.config["durations"]["break_duration"] = value
        self.save_config(self.config)

    def toggle_phase(self) -> str:
        """
        Toggle between work and break phases.

        Returns:
            str: Current phase as a string ("Work" or "Break").
        """
        self.is_work_phase = not self.is_work_phase
        return "Work" if self.is_work_phase else "Break"

    @property
    def finish_sound(self) -> str:
        """
        Retrieve the finish sound file path.

        Returns:
            str: Path to the finish sound.
        """
        return self.config["audio"].get("finish_sound", "sounds/default_finish.wav")

    @finish_sound.setter
    def finish_sound(self, value: str) -> None:
        """
        Set the finish sound file path.

        Args:
            value (str): Path to the finish sound.
        """
        self.config["audio"]["finish_sound"] = value
        self.save_config(self.config)

    @property
    def start_sound(self) -> str:
        """
        Retrieve the start sound file path.

        Returns:
            str: Path to the start sound.
        """
        return self.config["audio"].get("start_sound", "sounds/default_start.wav")

    @start_sound.setter
    def start_sound(self, value: str) -> None:
        """
        Set the start sound file path.

        Args:
            value (str): Path to the start sound.
        """
        self.config["audio"]["start_sound"] = value
        self.save_config(self.config)

    @property
    def stop_sound(self) -> str:
        """
        Retrieve the stop sound file path.

        Returns:
            str: Path to the stop sound.
        """
        return self.config["audio"].get("stop_sound", "sounds/default_stop.wav")

    @stop_sound.setter
    def stop_sound(self, value: str) -> None:
        """
        Set the stop sound file path.

        Args:
            value (str): Path to the stop sound.
        """
        self.config["audio"]["stop_sound"] = value
        self.save_config(self.config)

    @property
    def database_path(self):
        return self.config["todo"]["database_file_path"]

    @database_path.setter
    def database_path(self, value: str):
        self.config["todo"]["database_file_path"] = value
        self.save_config(self.config)
