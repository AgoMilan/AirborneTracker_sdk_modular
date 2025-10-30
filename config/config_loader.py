import os
import yaml


class ConfigLoader:
    """Loads and validates YAML configuration files."""

    @staticmethod
    def load(config_path):
        """Load configuration from YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("Invalid configuration format: expected dictionary")

        return data

    @staticmethod
    def load_config(config_path):
        """Alias for load(), for backward compatibility."""
        return ConfigLoader.load(config_path)

