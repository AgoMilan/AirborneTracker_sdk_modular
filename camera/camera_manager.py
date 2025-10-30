# Modul: camera/camera_manager.py
# camera/camera_manager.py
import cv2

class CameraManager:
    """Správa připojené kamery."""

    def __init__(self, source=0, width=None, height=None, fps=None):
        self.source = source
        self.cap = None
        self.width = width
        self.height = height
        self.fps = fps

    def start(self):
        """Inicializace kamery."""
        self.cap = cv2.VideoCapture(self.source)

        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.fps:
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not self.cap.isOpened():
            raise RuntimeError(f"Nelze otevřít kameru: {self.source}")

    def read(self):
        """Přečte jeden snímek z kamery."""
        if not self.cap:
            raise RuntimeError("Kamera není spuštěná. Zavolej nejprve .start().")
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Nepodařilo se získat snímek z kamery.")
        return frame

    def read_frame(self):
        """Alias pro kompatibilitu s main.py."""
        return self.read()

    def stop(self):
        """Ukončí práci s kamerou."""
        if self.cap:
            self.cap.release()
            self.cap = None


