# utils/config_loader.py
import yaml
from pathlib import Path

class ConfigLoader:
    """Načítá YAML konfiguraci a poskytuje přístup k parametrům."""

    @staticmethod
    def load_config(path: str):
        """Načte YAML konfiguraci a vrátí ji jako slovník."""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Konfigurační soubor nebyl nalezen: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return config

