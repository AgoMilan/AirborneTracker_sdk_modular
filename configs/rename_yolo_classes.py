# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 08:01:34 2025

@author: Milan
"""

from ultralytics import YOLO

# 🔹 Cesta ke starému modelu (ten bez názvů)
OLD_MODEL_PATH = r"C:\Users\Milan\Projekty\Trener_AOD4\runs\yolo_aod4_v1\yolo_aod4_v17\weights\best.pt"

# 🔹 Cesta k novému modelu s názvy
NEW_MODEL_PATH = r"C:\Users\Milan\Projekty\Cuda\AirborneTracker_sdk_modular\models\yolo8nAM150_named.pt"

# Načti model
model = YOLO(OLD_MODEL_PATH)
print("📦 Načten model:", OLD_MODEL_PATH)

# Přidej názvy tříd
model.model.names = {
    0: 'drone',
    1: 'bird',
    2: 'plane',
    3: 'helicopter'
}
print("🔠 Přidány názvy tříd:", model.model.names)

# 💾 Ulož nový model správně
model.save(NEW_MODEL_PATH)
print("✅ Nový model uložen:", NEW_MODEL_PATH)
