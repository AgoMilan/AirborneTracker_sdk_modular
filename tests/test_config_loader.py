# tests/test_config_loader.py
#Ověřuje, že YAML konfigurace (configs/default_config.yaml) 
#se načítá správně a obsahuje všechny očekávané sekce.

import os
import pytest
from config.config_loader import ConfigLoader


@pytest.fixture
def sample_config_file(tmp_path):
    """Vytvoří dočasný YAML config pro test."""
    yaml_content = """
    camera:
      source: 0
      width: 1280
      height: 720

    detection:
      model_path: "models/yolov8m_flying_objects.pt"
      classes: ["airplane", "drone", "bird"]
      confidence_thresh: 0.4

    tracking:
      max_lost: 10
      iou_threshold: 0.3

    logging:
      log_to_console: true
      log_to_file: false
      log_file_path: "data/logs/test_log.txt"
    """
    cfg_file = tmp_path / "test_config.yaml"
    cfg_file.write_text(yaml_content, encoding="utf-8")
    return cfg_file

def test_config_loader_reads_yaml(sample_config_file):
    """Ověří, že ConfigLoader načte YAML soubor bez chyb."""
    cfg = ConfigLoader.load(str(sample_config_file))
    assert isinstance(cfg, dict), "Načtená konfigurace není slovník!"
    assert "camera" in cfg, "Chybí sekce 'camera'!"
    assert "detection" in cfg, "Chybí sekce 'detection'!"
    assert "tracking" in cfg, "Chybí sekce 'tracking'!"
    assert "logging" in cfg, "Chybí sekce 'logging'!"

def test_camera_section_values(sample_config_file):
    """Kontrola, že hodnoty v sekci 'camera' jsou správného typu."""
    cfg = ConfigLoader.load(str(sample_config_file))
    cam = cfg["camera"]
    assert isinstance(cam["source"], int)
    assert cam["width"] == 1280
    assert cam["height"] == 720

def test_detection_section(sample_config_file):
    """Ověří, že detekční část obsahuje klíče a správné typy."""
    cfg = ConfigLoader.load(str(sample_config_file))
    det = cfg["detection"]

    assert "model_path" in det
    assert det["model_path"].endswith(".pt")
    assert isinstance(det["classes"], list)
    assert all(isinstance(c, str) for c in det["classes"])

def test_logging_defaults(sample_config_file):
    """Ověří, že logging sekce má správné typy a cesty."""
    cfg = ConfigLoader.load(str(sample_config_file))
    log = cfg["logging"]
    assert isinstance(log["log_to_console"], bool)
    assert isinstance(log["log_to_file"], bool)
    assert isinstance(log["log_file_path"], str)
