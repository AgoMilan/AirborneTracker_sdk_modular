# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 16:48:04 2025

@author: Milan
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 23:12:02 2025
Upraveno: přidána podpora pro více modelů a dynamické načítání tříd z configu
@author: Milan
"""

import torch
import numpy as np


class YoloAirborneDetector:
    """Wrapper pro YOLO model s podporou více modelů a konfigurace."""

    def __init__(self, model, config=None):
        self.model = model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.config = config or {}

        det_cfg = self.config.get("detection", {})
        self.conf_threshold = det_cfg.get("conf_threshold", 0.4)
        self.iou_threshold = det_cfg.get("iou_threshold", 0.5)

        # Určení aktivního modelu a jeho tříd
        self.active_model = det_cfg.get("active_model", "default")
        model_cfg = det_cfg.get("models", {}).get(self.active_model, {})

        # Načti seznam povolených tříd podle aktivního modelu
        self.allowed_classes = model_cfg.get("allowed_classes", det_cfg.get("allowed_classes", []))

        print(f"[YoloAirborneDetector] 🔧 Aktivní model: {self.active_model}")
        print(f"[YoloAirborneDetector] 🎯 Povolené třídy (ID): {self.allowed_classes}")
        print(f"[YoloAirborneDetector] ⚙️  conf={self.conf_threshold}, iou={self.iou_threshold}")

    def predict(self, image: np.ndarray):
        """Provede detekci a vrátí výsledky jako seznam slovníků."""
        try:
            results = self.model(
                image,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )

            detections = []
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                if self.allowed_classes and cls_id not in self.allowed_classes:
                    continue

                detections.append({
                    "bbox": box.xyxy[0].tolist(),
                    "conf": float(box.conf[0]),
                    "cls": self.model.names[cls_id],
                })

            return detections

        except Exception as e:
            print(f"[YoloAirborneDetector] ❌ Prediction failed: {e}")
            return []

    def detect(self, image: np.ndarray):
        """Alias pro kompatibilitu s main_GF.py"""
        return self.predict(image)
