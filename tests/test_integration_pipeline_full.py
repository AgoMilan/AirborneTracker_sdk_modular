# -*- coding: utf-8 -*-
# Cíl: integrační test celé pipeline 
#(ConfigLoader → ModelLoader → DetectorYOLO → inference).
"""
Created on Thu Oct 30 18:24:02 2025

@author: Milan
"""

import pytest
import numpy as np
from utils.config_loader import ConfigLoader
from detection.model_loader import ModelLoader
from detection.detector_yolo import DetectorYOLO

def test_full_detection_pipeline():
    """Test celé pipeline – načtení konfigurace, modelu a inference."""
    config = ConfigLoader.load_config("configs/default_config.yaml")
    model_path = config["detection"]["model_path"]

    model = ModelLoader.load_model(model_path)
    detector = DetectorYOLO(model)

    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    results = detector.predict(dummy_image)

    assert isinstance(results, list), "Výsledek pipeline není seznam."
    if len(results) > 0:
        first = results[0]
        assert all(k in first for k in ["bbox", "confidence", "class_name"]), "Chybí klíče ve výstupu."
