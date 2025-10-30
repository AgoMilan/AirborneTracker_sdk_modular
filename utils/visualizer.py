# utils/visualizer.py
import cv2
import time
import os

class Visualizer:
    def __init__(self, display=True, save_output=False, output_path="data/outputs/output.avi"):
        self.display = display
        self.save_output = save_output
        self.output_path = output_path
        self.writer = None
        self.fps_start_time = time.time()
        self.frame_count = 0
        self.last_fps = 0.0

    def _init_writer(self, frame):
        """Inicializuje zapisovač výstupního videa, pokud je potřeba."""
        if not self.save_output:
            return

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.writer = cv2.VideoWriter(self.output_path, fourcc, 25, (width, height))
        print(f"[Visualizer] Ukládám výstup do: {self.output_path}")

    def _update_fps(self):
        """Spočítá FPS každých 10 snímků."""
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            now = time.time()
            self.last_fps = 10 / (now - self.fps_start_time)
            self.fps_start_time = now
        return self.last_fps

    def draw(self, frame, detections, tracks=None):
        """Vykreslí detekce a případné tracky do snímku."""
        if frame is None:
            return frame

        # Inicializuj zapisovač, pokud je potřeba
        if self.writer is None and self.save_output:
            self._init_writer(frame)

        # --- Vykreslení detekcí ---
        for det in detections:
            x1, y1, x2, y2 = map(int, det["bbox"])
            label = det.get("label", "object")
            conf = det.get("confidence", 0.0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # --- Vykreslení tracků ---
        if tracks:
            for tr in tracks:
                if hasattr(tr, "bbox"):
                    x1, y1, x2, y2 = map(int, tr.bbox)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f"ID {tr.track_id}", (x1, y2 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # --- FPS overlay ---
        fps = self._update_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # --- Zobrazení a/nebo uložení ---
        if self.display:
            cv2.imshow("AirborneTracker", frame)

        if self.writer:
            self.writer.write(frame)

        return frame

    def close(self):
        """Uvolní prostředky."""
        if self.writer:
            self.writer.release()
            print("[Visualizer] Uložen výstupní soubor dokončen.")
        cv2.destroyAllWindows()
