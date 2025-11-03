# tools/camera_control_gui.py
"""
Simple PyQt6 GUI to control Canon camera and capture RAW/JPEG.
Requires: pip install PyQt6 opencv-python

Run:
    python -m tools.camera_control_gui
(or) python tools/camera_control_gui.py
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime

from PyQt6 import QtWidgets, QtGui, QtCore
import cv2
import numpy as np

# import Canon wrapper (adjust path if you placed file elsewhere)
try:
    from camera.camera_canon_raw import CanonCamera
except Exception as e:
    raise RuntimeError(f"Cannot import CanonCamera: {e}")

# Helper to convert cv2 BGR image to QImage
def cv2_to_qimage(frame):
    if frame is None:
        return None
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qt_img = QtGui.QImage(rgb.data, w, h, 3 * w, QtGui.QImage.Format.Format_RGB888)
    return qt_img

class CameraWorker(QtCore.QObject):
    frame_ready = QtCore.pyqtSignal(np.ndarray)
    error = QtCore.pyqtSignal(str)

    def __init__(self, cam: CanonCamera, parent=None):
        super().__init__(parent)
        self.cam = cam
        self.running = False
        self._interval = 0.05  # 50 ms

    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            try:
                frame = self.cam.get_frame()
                if frame is not None:
                    self.frame_ready.emit(frame)
                time.sleep(self._interval)
            except Exception as e:
                self.error.emit(str(e))
                time.sleep(0.2)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, sdk_path: str, debug: bool = False):
        super().__init__()
        self.setWindowTitle("Canon LiveView & RAW capture")
        self.resize(1000, 600)

        self.cam = CanonCamera(sdk_path=sdk_path, debug=debug)
        try:
            self.cam.initialize()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize camera: {e}")

        # UI
        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(800, 600)
        self.image_label.setStyleSheet("background: black;")

        # controls
        self.btn_start_live = QtWidgets.QPushButton("Start LiveView")
        self.btn_stop_live = QtWidgets.QPushButton("Stop LiveView")
        self.btn_raw = QtWidgets.QPushButton("Capture RAW")
        self.btn_jpg = QtWidgets.QPushButton("Capture JPEG")
        self.btn_quit = QtWidgets.QPushButton("Quit")

        self.iso_combo = QtWidgets.QComboBox()
        self.iso_combo.addItems(["100", "200", "400", "800", "1600", "3200"])
        self.iso_combo.setCurrentText("400")

        self.shutter_combo = QtWidgets.QComboBox()
        self.shutter_combo.addItems(["1/8000","1/4000","1/2000","1/1000","1/500","1/250","1/125","1/60","1/30","1/15"])
        self.shutter_combo.setCurrentText("1/125")

        self.aperture_combo = QtWidgets.QComboBox()
        self.aperture_combo.addItems(["1.4","2.0","2.8","4.0","5.6","8.0","11"])
        self.aperture_combo.setCurrentText("5.6")

        self.wb_combo = QtWidgets.QComboBox()
        self.wb_combo.addItems(["Auto","Daylight","Cloudy","Tungsten","Fluorescent"])
        self.wb_combo.setCurrentText("Daylight")

        controls_layout = QtWidgets.QFormLayout()
        controls_layout.addRow("ISO", self.iso_combo)
        controls_layout.addRow("Shutter", self.shutter_combo)
        controls_layout.addRow("Aperture", self.aperture_combo)
        controls_layout.addRow("WhiteBalance", self.wb_combo)
        controls_layout.addRow(self.btn_raw, self.btn_jpg)
        controls_layout.addRow(self.btn_start_live, self.btn_stop_live)
        controls_layout.addRow(self.btn_quit)

        hl = QtWidgets.QHBoxLayout(self)
        hl.addWidget(self.image_label)
        hl.addLayout(controls_layout)

        # events
        self.btn_start_live.clicked.connect(self.on_start_live)
        self.btn_stop_live.clicked.connect(self.on_stop_live)
        self.btn_raw.clicked.connect(self.on_capture_raw)
        self.btn_jpg.clicked.connect(self.on_capture_jpeg)
        self.btn_quit.clicked.connect(self.close_app)

        self.worker = None
        self.thread = None

        # output folder
        self.out_dir = Path("data/raw")
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def on_start_live(self):
        try:
            self.cam.start_liveview()
            # start worker
            if self.worker is None:
                self.worker = CameraWorker(self.cam)
                self.worker.frame_ready.connect(self.on_frame_ready)
                self.worker.error.connect(self.on_worker_error)
            self.worker.start()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Start LiveView", f"Error: {e}")

    def on_stop_live(self):
        try:
            if self.worker:
                self.worker.stop()
            self.cam.stop_liveview()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Stop LiveView", f"Warning: {e}")

    def on_frame_ready(self, frame: np.ndarray):
        qimg = cv2_to_qimage(frame)
        if qimg is None:
            return
        pix = QtGui.QPixmap.fromImage(qimg).scaled(self.image_label.size(),
                                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pix)

    def on_worker_error(self, msg):
        print("[CameraWorker] Error:", msg)

    def on_capture_raw(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = self.out_dir / f"{ts}.CR2"
        try:
            self.cam.capture_raw(str(out))
            QtWidgets.QMessageBox.information(self, "RAW saved", f"Saved: {out}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "RAW error", str(e))

    def on_capture_jpeg(self):
        # capture currently displayed frame as jpeg
        frame = self.cam.get_frame()
        if frame is None:
            QtWidgets.QMessageBox.warning(self, "No frame", "No LiveView frame available.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = self.out_dir / f"{ts}.jpg"
        cv2.imwrite(str(out), frame)
        QtWidgets.QMessageBox.information(self, "JPEG saved", f"Saved: {out}")

    def close_app(self):
        try:
            if self.worker:
                self.worker.stop()
            self.cam.stop_liveview()
            self.cam.close()
        except Exception:
            pass
        QtWidgets.QApplication.quit()

def main():
    # find SDK path in config if possible, else edit here
    sdk_path = None
    try:
        from config.config_loader import ConfigLoader
        cfg = ConfigLoader.load_config("configs/default_config.yaml")
        sdk_path = cfg.get("camera", {}).get("edsdk_path") or cfg.get("edsdk_path")
    except Exception:
        sdk_path = None

    if not sdk_path:
        # <- EDIT HERE if your config does not provide EDSDK path:
        sdk_path = r"C:\Users\Milan\Projekty\Cuda\EDSDKv131910W\Windows\EDSDK_64\Dll\EDSDK.dll"

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(sdk_path=sdk_path, debug=True)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
