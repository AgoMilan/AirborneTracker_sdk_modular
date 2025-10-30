# -*- coding: utf-8 -*-
# Cíl: ověřit, že konfigurace se dá správně načíst a obsahuje potřebné klíče
"""
Created on Thu Oct 30 18:21:46 2025

@author: Milan
"""
import pytest
import os
from config.config_loader import ConfigLoader


def test_config_file_exists():
    """Ověř, že konfigurační soubor existuje."""
    assert os.path.exists("configs/default_config.yaml"), "Soubor configs/default_config.yaml chybí!"

def test_config_structure():
    """Ověř, že konfigurace obsahuje potřebné sekce."""
    config = ConfigLoader.load_config("configs/default_config.yaml")
    assert "detection" in config, "V konfiguraci chybí sekce 'detection'."
    assert "model_path" in config["detection"], "V sekci 'detection' chybí 'model_path'."


