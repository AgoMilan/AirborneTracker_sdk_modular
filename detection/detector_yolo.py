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
            results = self.model(image)
            detections = []
            for r in results[0].boxes:
                detections.append({
                    "bbox": r.xyxy[0].tolist(),
                    "conf": float(r.conf[0]),
                    "cls": int(r.cls[0]),
                })
            return detections
        except Exception as e:
            print(f"[YoloAirborneDetector] Prediction failed: {e}")
            return []

    def detect(self, image: np.ndarray):
        """Alias pro kompatibilitu s main.py."""
        return self.predict(image)
