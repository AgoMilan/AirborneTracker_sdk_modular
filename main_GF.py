# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 12:07:51 2025

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
    logging.info("[main_G] ✅ Konfigurace načtena.")

    # === Cesty ===
    sdk_path = r"C:\Users\Milan\Projekty\Cuda\EDSDKv131910W\Windows\EDSDK_64\Dll\EDSDK.dll"
    model_path = os.path.join("models", "yolov8n.pt")

    if not os.path.exists(model_path):
        logging.error(f"❌ Modelový soubor nebyl nalezen: {model_path}")
        sys.exit(1)

    # === Inicializace YOLO modelu ===
    logging.info(f"Načítám YOLO model z: {model_path}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"✅ CUDA detekována – model poběží na {device.upper()}")

    try:
        model = YOLO(model_path)  # ← načte pouze lokální soubor
        model.to(device)
        logging.info(f"✅ YOLO model úspěšně načten z lokálního disku ({model_path})")
    except Exception as e:
        logging.error(f"❌ Chyba při načítání YOLO modelu: {e}")
        sys.exit(1)

    # === Inicializace detektoru ===
    detector = YoloAirborneDetector(model, config)
    logging.info("[main_G] ✅ Detektor inicializován.")

    # === Spuštění GUI (bez trackeru) ===
    run_gui(
        sdk_path=sdk_path,
        detector=detector
    )


if __name__ == "__main__":
    main()
