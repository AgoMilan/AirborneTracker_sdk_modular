# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 16:53:26 2025

@author: Milan
"""

# tests/test_model_loader.py
import os
import pytest
import numpy as np
from detection.model_loader import ModelLoader

@pytest.fixture(scope="session")
def model_path():
    """Cesta k testovacímu YOLO modelu."""
    # Přizpůsob si cestu podle své struktury
    path = os.path.abspath("models/yolov8n.pt")
    if not os.path.exists(path):
        pytest.skip(f"Model '{path}' nebyl nalezen – test přeskočen.")
    return path


def test_model_loads_successfully(model_path):
    """Ověř, že YOLO model se načte bez chyby a má očekávané atributy."""
    model = ModelLoader.load_model(model_path)
    assert model is not None, "Model se nenačetl!"
    assert hasattr(model, "predict"), "Model nemá metodu 'predict'!"
    assert hasattr(model, "names"), "Model nemá atribut 'names'!"
    assert isinstance(model.names, dict), "Atribut 'names' nemá očekávaný typ dict!"


def test_model_prediction_on_dummy_image(model_path):
    """Ověř, že model zvládne predikci na náhodném obrázku."""
    model = ModelLoader.load_model(model_path)

    # Vytvoř jednoduchý náhodný obrázek (640x640 RGB)
    dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    results = model.predict(source=dummy_img, verbose=False)
    assert results is not None, "Model nevrátil žádné výsledky!"
    assert hasattr(results[0], "boxes"), "Výsledek nemá atribut 'boxes'!"

    # Výsledek může být prázdný (žádná detekce), ale musí být validní
    assert isinstance(results[0].boxes.xyxy, np.ndarray) or hasattr(results[0].boxes, "xyxy"), \
        "Výsledek predikce nemá správný formát!"

