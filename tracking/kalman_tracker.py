# tracking/object_tracking_manager.py
from tracking.kalman_tracker import KalmanTracker

class ObjectTrackingManager:
    def __init__(self, max_lost=10, iou_threshold=0.3):
        self.max_lost = max_lost
        self.iou_threshold = iou_threshold
        self.trackers = {}

    def update(self, detections, frame_id):
        # TODO: implementace IOU párování
        # Zatím jen placeholder
        for det in detections:
            print(f"[TrackingManager] Frame {frame_id}: detekce {det['label']} @ {det['bbox']}")

    def get_active_tracks(self):
        # Vrací aktuálně sledované objekty
        return list(self.trackers.values())

    def remove_lost_tracks(self):
        # TODO: implementace odebrání ztracených tracků
        pass

