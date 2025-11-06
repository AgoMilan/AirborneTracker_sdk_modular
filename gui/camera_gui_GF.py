# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 16:41:31 2025

@author: Milan
"""

# -*- coding: utf-8 -*-
"""
Updated on Mon Nov  3 2025
@author: Milan
"""

import sys
import os
import time
import cv2
import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets

from camera.camera_canon_G import CanonCamera


class CameraWorker(QtCore.QThread):
    """Vlákno pro získávání snímků z kamery."""
    frame_ready = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.running = False

    def run(self):
        print("[CameraWorker] Smyčka spuštěna.")
        self.running = True
        while self.running:
            frame = self.camera.get_frame()
            if frame is not None:
                self.frame_ready.emit(frame)
            time.sleep(0.05)
        print("[CameraWorker] Smyčka ukončena.")

    def stop(self):
        self.running = False


class DetectorWorker(QtCore.QThread):
    """Vlákno pro YOLO detekci."""
    detection_ready = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.running = False
        self.last_frame = None

    def set_frame(self, frame):
        self.last_frame = frame

    def run(self):
        print("[DetectorWorker] Smyčka spuštěna.")
        self.running = True
        while self.running:
            if self.last_frame is not None and self.detector is not None:
                try:
                    detections = self.detector.detect(self.last_frame)
                    vis = self.last_frame.copy()
                    for det in detections:
                        x1, y1, x2, y2 = map(int, det["bbox"])
                        conf = det["conf"]
                        cls = det["cls"]
                        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            vis,
                            f"{cls}:{conf:.2f}",
                            (x1, max(10, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            1,
                            cv2.LINE_AA,
                        )
                    self.detection_ready.emit(vis)
                    self.last_frame = None
                except Exception as e:
                    print(f"[DetectorWorker] ⚠️ Chyba při detekci: {e}")
                    time.sleep(0.05)
            time.sleep(0.03)
        print("[DetectorWorker] Smyčka ukončena.")

    def stop(self):
        self.running = False


class CameraGUI(QtWidgets.QMainWindow):
    """Hlavní GUI aplikace."""
    def __init__(self, sdk_path, detector=None):
        super().__init__()

        self.setWindowTitle("AirborneTracker GUI")
        self.sdk_path = sdk_path
        self.detector = detector
        self.cam = None
        self.last_frame = None

        print("[GUI] ✅ Inicializováno.")
        print("[GUI] ▶️ Spouštím Canon kameru...")

        # 🟢 Inicializace kamery
        try:
            self.cam = CanonCamera(self.sdk_path, debug=True)
            self.cam.initialize()
            self.cam.start_liveview()
            print("[GUI] ✅ Kamera inicializována a LiveView běží.")
        except Exception as e:
            print(f"[GUI] ❌ Chyba při inicializaci kamery: {e}")
            self.cam = None

        # GUI komponenty
        self._setup_ui()

        # Vlákna
        self.camera_thread = None
        self.detector_thread = None

    def _setup_ui(self):
        """Vytvoření GUI prvků."""
        self.video_label = QtWidgets.QLabel()
        self.video_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")

        self.start_button = QtWidgets.QPushButton("Start")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.save_button = QtWidgets.QPushButton("Uložit snímek")
        self.quit_button = QtWidgets.QPushButton("Quit")

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.save_button.clicked.connect(self.save_frame)
        self.quit_button.clicked.connect(self.close)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.quit_button)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.resize(800, 600)

    def start_camera(self):
        print("[GUI] ▶️ Start kamery požadován.")

        # 🟢 Pokus o znovuspuštění LiveView (Canon SDK)
        if self.cam:
            try:
                self.cam.start_liveview()
            except Exception as e:
                print(f"[GUI] ⚠️ Nepodařilo se znovu spustit LiveView: {e}")

        # 🟢 Znovuvytvoření vláken
        if not self.camera_thread or not self.camera_thread.isRunning():
            self.camera_thread = CameraWorker(self.cam)
            self.camera_thread.frame_ready.connect(self.update_view)
            self.camera_thread.frame_ready.connect(self._set_frame_for_detector)
            self.camera_thread.start()
            print("[GUI] ✅ Kamera thread spuštěn.")

        if not self.detector_thread or not self.detector_thread.isRunning():
            self.detector_thread = DetectorWorker(self.detector)
            self.detector_thread.detection_ready.connect(self.update_view)
            self.detector_thread.start()
            print("[GUI] ✅ Detekční thread spuštěn.")

    def _set_frame_for_detector(self, frame):
        if self.detector_thread:
            self.detector_thread.set_frame(frame)

    def stop_camera(self):
        print("[GUI] 🛑 Stop LiveView požadavek.")

        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.finished.connect(lambda: print("[CameraWorker] 🔚 Ukončen."))
            self.camera_thread = None

        if self.detector_thread:
            self.detector_thread.stop()
            self.detector_thread.finished.connect(lambda: print("[DetectorWorker] 🔚 Ukončen."))
            self.detector_thread = None

        if self.cam:
            try:
                self.cam.stop_liveview()
            except Exception as e:
                print(f"[GUI] ⚠️ Chyba při zastavení kamery: {e}")

    def save_frame(self):
        """Uloží aktuální snímek do složky 'foto'."""
        if self.last_frame is None:
            print("[GUI] ⚠️ Není co uložit – žádný snímek není k dispozici.")
            return
        os.makedirs("foto", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join("foto", f"snimek_{timestamp}.jpg")
        cv2.imwrite(filename, self.last_frame)
        print(f"[GUI] 💾 Snímek uložen: {filename}")

    def update_view(self, frame):
        """Aktualizace zobrazeného obrazu."""
        if frame is None:
            return
        self.last_frame = frame.copy()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qimg)
        self.video_label.setPixmap(
            pix.scaled(self.video_label.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        )
        print(f"[GUI] ✅ Zobrazeno {w}x{h}")

    def closeEvent(self, event):
        """Bezpečné ukončení GUI a kamery."""
        print("[GUI] 🛑 Zavírám okno...")
        self.stop_camera()
        if self.cam:
            try:
                self.cam.close()
            except Exception as e:
                print(f"[GUI] ⚠️ Chyba při ukončování kamery: {e}")
        print("[GUI] Ukončuji aplikaci...")
        event.accept()


def run_gui(sdk_path, detector=None):
    """Spuštění GUI aplikace."""
    print(f"[run_gui] sdk_path={sdk_path}")
    app = QtWidgets.QApplication(sys.argv)
    gui = CameraGUI(sdk_path, detector=detector)
    gui.show()
    sys.exit(app.exec())
