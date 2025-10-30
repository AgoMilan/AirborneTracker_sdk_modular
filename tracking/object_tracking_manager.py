# tracking/object_tracking_manager.py
from tracking.kalman_tracker import KalmanTracker
from ultralytics import YOLO

class ObjectTrackingManager:
    def __init__(self, max_lost=10, iou_threshold=0.3):
        self.max_lost = max_lost
        self.iou_threshold = iou_threshold
        self.trackers = {}
        self.model = YOLO("models/yolov8n.pt")  # načteme pro mapování ID -> názvu třídy

    def update(self, detections, frame_id):
        """
        Aktualizuje seznam sledovaných objektů podle detekcí.
        Zatím jen loguje výstup YOLO detekcí.
        """
        if not detections:
            print(f"[TrackingManager] Frame {frame_id}: žádné detekce.")
            return

        for det in detections:
            # Přečti název třídy
            label = det.get("label")
            if label is None:
                cls_id = det.get("cls")
                if cls_id is not None and hasattr(self.model, "names"):
                    label = self.model.names.get(int(cls_id), f"class_{cls_id}")
                else:
                    label = "unknown"

            bbox = det.get("bbox", [])
            conf = det.get("confidence", None)

            print(f"[TrackingManager] Frame {frame_id}: detekce {label} @ {bbox} (conf={conf})")

        # TODO: zde doplnit přiřazení detekcí k existujícím trackerům (např. pomocí IOU)
        # např.:
        # self._match_detections_to_trackers(detections)

    def get_active_tracks(self):
        """Vrací aktuálně sledované objekty."""
        return list(self.trackers.values())

    def remove_lost_tracks(self):
        """Odebere trackery, které ztratily objekt."""
        # TODO: implementace odebrání ztracených tracků
        pass
