from pathlib import Path

import toml
from loguru import logger


class AppState:
    """
    Manages the application state and configurations.

    Args:
        config_path (Path): Path to the configuration file.
    """

    def __init__(self, config_path: Path, debug_mode: bool):
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
                "durations": {"work_duration": 1500, "break_duration": 300}
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
        @brief Retrieve the work duration.
        @return Work duration in seconds.
        """
        return self.config["durations"]["work_duration"]

    @work_duration.setter
    def work_duration(self, value: int) -> None:
        """
        @brief Set the work duration.
        @param value New work duration in seconds.
        """
        self.config["durations"]["work_duration"] = value
        self.save_config(self.config)

    @property
    def break_duration(self) -> int:
        """
        @brief Retrieve the break duration.
        @return Break duration in seconds.
        """
        return self.config["durations"]["break_duration"]

    @break_duration.setter
    def break_duration(self, value: int) -> None:
        """
        @brief Set the break duration.
        @param value New break duration in seconds.
        """
        self.config["durations"]["break_duration"] = value
        self.save_config(self.config)

    def toggle_phase(self) -> str:
        """
        @brief Toggle between work and break phases.
        @return Current phase as a string ("Work" or "Break").
        """
        self.is_work_phase = not self.is_work_phase
        return "Work" if self.is_work_phase else "Break"

    @property
    def finish_sound(self) -> str:
        """
        @brief Retrieve the finish sound file path.
        @return Path to the finish sound.
        """
        return self.config.get("audio", {}).get("finish_sound", "sounds/default_sound.wav")

    @finish_sound.setter
    def finish_sound(self, value: str) -> None:
        """
        @brief Set the finish sound file path.
        @param value Path to the finish sound.
        """
        if "audio" not in self.config:
            self.config["audio"] = {}
        self.config["audio"]["finish_sound"] = value
        self.save_config(self.config)
