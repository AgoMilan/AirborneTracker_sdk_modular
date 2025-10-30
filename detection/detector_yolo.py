import torch
import numpy as np


class DetectorYOLO:
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
            results = self.model.predict(
                source=image,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                device=self.device,
                verbose=False
            )

            detections = []
            for r in results:
                boxes = getattr(r, "boxes", [])
                if boxes is None:
                    continue
                for b in boxes:
                    cls_id = int(b.cls[0])
                    conf = float(b.conf[0])
                    x1, y1, x2, y2 = map(float, b.xyxy[0])
                    detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "class_name": self.model.names[cls_id],
                    })
            return detections
        except Exception as e:
            raise RuntimeError(f"YOLO prediction failed: {e}")
            
    def detect_objects(self, image):
        """Alias for predict() for compatibility with pipeline tests."""
        return self.predict(image)