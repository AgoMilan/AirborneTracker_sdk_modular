# tracking/object_tracking_manager.py
from tracking.kalman_tracker import KalmanTracker

class ObjectTrackingManager:
    def __init__(self, max_lost=10, iou_threshold=0.3, debug=False):
        """
        Správce objektového sledování (tracking).
        """
        self.max_lost = max_lost
        self.iou_threshold = iou_threshold
        self.trackers = {}
        self.debug = debug

    def update(self, detections, frame_id):
        """Zpracování nových detekcí a aktualizace trackerů."""
        if not detections:
            if self.debug:
                print(f"[TrackingManager] Frame {frame_id}: žádné detekce.")
            return

        for det in detections:
            label = det.get('label', det.get('class', 'unknown'))
            bbox = det.get('bbox')
            conf = det.get('confidence', None)
            if self.debug:
                print(f"[TrackingManager] Frame {frame_id}: detekce {label} @ {bbox} (conf={conf})")

    def get_active_tracks(self):
        """Vrací aktuálně sledované objekty."""
        return list(self.trackers.values())

    def remove_lost_tracks(self):
        """Odstraní ztracené tracky (zatím placeholder)."""
        pass
