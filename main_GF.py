# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 12:07:51 2025
Upraveno: přidána možnost výběru dvou modelů YOLO (standardní a M150)
@author: Milan
"""

import os
import sys
import torch
import logging
from datetime import datetime

# --- Vlastní moduly ---
from detection.detector_yolo import YoloAirborneDetector
from gui.camera_gui_G import run_gui
from utils.config_loader import ConfigLoader
from utils.logger_G import setup_logger
from ultralytics import YOLO


def main():
    print("\n=== AirborneTracker GUI verze ===")

    # === Inicializace logování ===
    os.makedirs("data/logs", exist_ok=True)
    log_filename = os.path.join("data/logs", f"tracker_log_{datetime.now().strftime('%Y%m%d')}.txt")
    setup_logger(log_filename)
    logging.info(f"[Logger] Logování do souboru: {log_filename}")

    # === Načtení konfigurace ===
    cfg_path = "configs/default_config.yaml"
    config = ConfigLoader.load_config(cfg_path)
    logging.info("[main_GF] ✅ Konfigurace načtena.")

    # === Cesty ===
    sdk_path = r"C:\Users\Milan\Projekty\Cuda\EDSDKv131910W\Windows\EDSDK_64\Dll\EDSDK.dll"

    # === Definuj oba modely ===
    model_default = os.path.join("models", "yolov8n.pt")
    model_m150 = os.path.join("models", "yolo8nM150.pt")

    # --- Zjisti, který model použít ---
    # 1️⃣ Nejprve z konfigurace (pokud existuje klíč)
    active_model = "default"
    if "detection" in config and "active_model" in config["detection"]:
        active_model = config["detection"]["active_model"]

    # 2️⃣ Přepnutí z příkazové řádky (např. python main_GF.py m150)
    if len(sys.argv) > 1 and sys.argv[1].lower() == "m150":
        active_model = "m150"

    # 3️⃣ Nastav cestu k modelu podle volby
    if active_model == "m150":
        model_path = model_m150
    else:
        model_path = model_default

    logging.info(f"[main_GF] 🔍 Aktivní model: {active_model.upper()} -> {model_path}")

    if not os.path.exists(model_path):
        logging.error(f"❌ Modelový soubor nebyl nalezen: {model_path}")
        sys.exit(1)

    # === Inicializace YOLO modelu ===
    logging.info(f"Načítám YOLO model z: {model_path}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"✅ Použité zařízení: {device.upper()}")

    try:
        model = YOLO(model_path)
        model.to(device)
        logging.info(f"✅ YOLO model úspěšně načten ({model_path})")
    except Exception as e:
        logging.error(f"❌ Chyba při načítání YOLO modelu: {e}")
        sys.exit(1)

    # === Inicializace detektoru ===
    detector = YoloAirborneDetector(model, config)
    logging.info("[main_GF] ✅ Detektor inicializován.")

    # === Spuštění GUI (bez trackeru) ===
    run_gui(
        sdk_path=sdk_path,
        detector=detector
    )


if __name__ == "__main__":
    main()
