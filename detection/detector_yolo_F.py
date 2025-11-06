# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 23:12:02 2025

@author: Milan
"""

# detection/detector_yolo.py

import torch
import numpy as np

class YoloAirborneDetector:
    """Wrapper for YOLO model."""

    def __init__(self, model, config=None):
        self.model = model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if config is None:
            self.conf_threshold = 0.4
            self.iou_threshold = 0.5
        else:
            self.conf_threshold = config.get("detection", {}).get("confidence_threshold", 0.4)
            self.iou_threshold = config.get("detection", {}).get("iou_threshold", 0.5)

    def predict(self, image: np.ndarray):
        """Return predictions as list of dicts."""
        try:
            results = self.model(image, verbose=False)  # verbose=False potlačí vípisy do konzole
            detections = []
            # 🛫 Povolené třídy – lze přidat víc (např. "drone", "bird" apod.)
            ALLOWED_CLASS_IDS = [4, 14]
            
            for r in results[0].boxes:
                cls_id = int(r.cls[0])
                if cls_id not in ALLOWED_CLASS_IDS:
                    continue

                detections.append({
                "bbox": r.xyxy[0].tolist(),
                "conf": float(r.conf[0]),
                "cls": self.model.names[cls_id],
            })
            return detections
        except Exception as e:
            print(f"[YoloAirborneDetector] Prediction failed: {e}")
            return []

    def detect(self, image: np.ndarray):
        """Alias pro kompatibilitu s main.py."""
        return self.predict(image)