# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 17:13:36 2025

@author: Milan
"""

# tests/test_pipeline_detection.py
import os
import pytest
import numpy as np

from utils.config_loader import ConfigLoader
from detection.model_loader import ModelLoader
from detection.detector_yolo import DetectorYOLO


@pytest.fixture(scope="session")
def pipeline_components():
    """Inicializuje komponenty pipeline (ConfigLoader, ModelLoader, DetectorYOLO)."""
    # 1️⃣ Načtení konfigurace
    config = ConfigLoader.load_config("configs/default_config.yaml")
    model_path = config["detection"]["model_path"]
    assert os.path.exists(model_path), f"Model '{model_path}' neexistuje!"

    # 2️⃣ Načtení modelu
    model = ModelLoader.load_model(model_path)
    assert model is not None, "Model se nepodařilo načíst."

    # 3️⃣ Inicializace detektoru
    detector = DetectorYOLO(model, config)

    return config, model, detector


def test_pipeline_initialization(pipeline_components):
    """Ověř, že pipeline komponenty jsou inicializovány správně."""
    config, model, detector = pipeline_components

    assert "detection" in config, "Konfigurace neobsahuje sekci 'detection'."
    assert hasattr(model, "predict"), "Model nemá metodu predict!"
    assert hasattr(detector, "detect_objects"), "Třída DetectorYOLO postrádá metodu detect_objects!"


def test_pipeline_detection_on_dummy_image(pipeline_components):
    """Ověř, že pipeline zvládne detekci na testovacím obrázku."""
    _, _, detector = pipeline_components

    # 640x640 náhodný testovací obrázek
    dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    detections = detector.detect_objects(dummy_img)

    assert detections is not None, "Detekce vrátila None!"
    assert isinstance(detections, list), "Výsledek detekce není list!"
    assert all(isinstance(det, dict) for det in detections), "Každá detekce by měla být slovník!"
    # Výsledek může být prázdný, ale musí být validní
    print(f"Počet detekcí: {len(detections)}")
