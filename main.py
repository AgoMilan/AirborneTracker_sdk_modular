# main.py

import time
import cv2
import yaml

from camera.camera_manager import CameraManager
from detection.model_loader import ModelLoader
from detection.detector_yolo import YoloAirborneDetector
from tracking.object_tracking_manager import ObjectTrackingManager
from utils.config_loader import ConfigLoader
from utils.logger import AppLogger
from utils.visualizer import Visualizer
from utils.performance_timer import PerformanceTimer
from utils.logger import Logger

def main():
    # 1. Načti konfiguraci
    cfg = ConfigLoader.load("configs/default_config.yaml")
    
    logger_cfg = cfg["logging"]
    logger = Logger(
        log_to_console=logger_cfg["log_to_console"],
        log_to_file=logger_cfg["log_to_file"],
        log_file_path=logger_cfg["log_file_path"]
        )

    logger.info("AirborneTracker SDK startuje...")    

    # 2. Nastav logger
    logger = AppLogger(cfg["logging"])

    # 3. Načti model
    model = ModelLoader.load_model(cfg["detection"]["model_path"])
    detector = YoloAirborneDetector(model, classes=cfg["detection"]["classes"],
                                     confidence_thresh=cfg["detection"]["confidence_thresh"],
                                     iou_thresh=cfg["detection"]["iou_thresh"])

    # 4. Inicializuj kameru / video
    cam = CameraManager(cfg["camera"]["source"], width=cfg["camera"]["width"],
                        height=cfg["camera"]["height"], fps=cfg["camera"].get("fps", None))
    cam.start()

    # 5. Inicializuj tracker
    tracker_mgr = ObjectTrackingManager(max_lost=cfg["tracking"]["max_lost"],
                                        iou_threshold=cfg["tracking"]["iou_threshold"])

    # 6. Vizualizátor
    visualizer = Visualizer(display=cfg["visualizer"]["display"],
                            save_output=cfg["visualizer"]["save_output"],
                            output_path=cfg["visualizer"]["output_path"])

    # 7. Výkonnostní měření
    perf_timer = PerformanceTimer()

    frame_id = 0
    try:
        while True:
            frame = cam.read_frame()
            if frame is None:
                break

            frame_id += 1
            perf_timer.start()

            # Detekce
            detections = detector.detect(frame)

            # Sledování
            tracker_mgr.update(detections, frame_id)
            tracks = tracker_mgr.get_active_tracks()

            # Vizualizace
            visualizer.draw(frame, detections, tracks)

            # Logování
            for tr in tracks:
                logger.log(f"Frame {frame_id}, TrackID {tr.track_id}, BBox {tr.bbox}, Class {tr.cls}, Confidence {tr.confidence}")

            perf_timer.stop()

            # Volitelné: uložení nebo přerušení smyčky
            if cfg["camera"].get("max_frames") and frame_id >= cfg["camera"]["max_frames"]:
                break

            # Zobrazení
            if cfg["visualizer"]["display"]:
                cv2.imshow("AirborneTracker", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cam.stop()
        cv2.destroyAllWindows()

    except KeyboardInterrupt:
        cam.stop()
        cv2.destroyAllWindows()
        logger.log("Interrupted by user")

    logger.log(f"Processed {frame_id} frames. Avg FPS: {perf_timer.get_fps():.2f}")

if __name__ == "__main__":
    main()
