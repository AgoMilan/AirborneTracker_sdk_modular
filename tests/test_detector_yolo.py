# -*- coding: utf-8 -*-
# Otestuje samotný detekční modul (DetectorYOLO) —
# načítání modelu, inference a formát výstupu
"""
Created on Thu Oct 30 18:17:41 2025

@author: Milan
"""

import pytest
import numpy as np
import torch
from detection.detector_yolo import DetectorYOLO
from detection.model_loader import ModelLoader

@pytest.fixture(scope="session")
def detector():
    """Inicializuje YOLO detektor s malým testovacím modelem."""
    model_path = "models/yolov8n.pt"  # uprav dle svého modelu
    model = ModelLoader.load_model(model_path)
    return DetectorYOLO(model)

def test_detector_initialization(detector):
    """Ověř, že detektor má načtený model a běží na správném zařízení."""
    assert hasattr(detector, "model"), "Detektor nemá atribut 'model'."
    assert detector.model is not None, "Model není inicializován."
    assert detector.device in ["cpu", "cuda"], f"Neznámé zařízení: {detector.device}"

def test_detector_prediction_shape(detector):
    """Ověř, že predikce na dummy obrázku vrací výsledek."""
    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    results = detector.predict(dummy_image)
    assert results is not None, "Predikce vrátila None."
    assert isinstance(results, list), "Výsledek by měl být seznam."
    assert all(isinstance(r, dict) for r in results), "Každý výsledek musí být dict."
