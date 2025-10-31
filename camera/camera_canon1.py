# camera/camera_canon.py
import os
import time
import ctypes
import numpy as np
import cv2
from utils.config_loader import ConfigLoader


# Canon EDSDK konstanty
EDS_OK = 0x00000000
kEdsPropID_Evf_OutputDevice = 0x00000500
kEdsEvfOutputDevice_PC = 0x00000002
kEdsPropID_Record = 0x00000501
kEdsRecord_Stop = 0
kEdsRecord_Start = 4


class CanonCamera:
    """Canon EOS LiveView kamera přes EDSDK."""

    def __init__(self, sdk_path, debug=False):
        self.debug = debug
        self.sdk_path = sdk_path
        self.edsdk = None
        self.cam_ref = None
        self.available = False
        self.initialized = False

        if not os.path.exists(sdk_path):
            raise FileNotFoundError(f"[CanonCamera] SDK knihovna nenalezena: {sdk_path}")

        try:
            self.edsdk = ctypes.WinDLL(sdk_path)
            print(f"[CanonCamera] EDSDK načteno z: {sdk_path}")
            self.available = True
        except Exception as e:
            raise RuntimeError(f"[CanonCamera] Nelze načíst EDSDK DLL: {e}")

    def initialize(self):
        """Inicializace EDSDK a otevření relace s kamerou."""
        if not self.available:
            raise RuntimeError("[CanonCamera] SDK není k dispozici")

        print("[CanonCamera] Inicializuji EDSDK...")
        self._check(self.edsdk.EdsInitializeSDK(), "EdsInitializeSDK")

        cam_list = ctypes.c_void_p()
        self._check(self.edsdk.EdsGetCameraList(ctypes.byref(cam_list)), "EdsGetCameraList")

        cam_ref = ctypes.c_void_p()
        self._check(self.edsdk.EdsGetChildAtIndex(cam_list, 0, ctypes.byref(cam_ref)), "EdsGetChildAtIndex")

        # Uvolnit seznam kamer
        try:
            self.edsdk.EdsRelease(cam_list)
        except Exception:
            pass

        # Otevřít relaci
        self._check(self.edsdk.EdsOpenSession(cam_ref), "EdsOpenSession")
        self.cam_ref = cam_ref
        self.initialized = True
        print("[CanonCamera] ✅ Session otevřena.")

    def start_liveview(self):
        """Spuštění LiveView režimu."""
        if not self.initialized:
            raise RuntimeError("[CanonCamera] Nelze spustit LiveView – kamera není inicializována.")

        output_device = ctypes.c_int(kEdsEvfOutputDevice_PC)
        result = self.edsdk.EdsSetPropertyData(
            self.cam_ref, kEdsPropID_Evf_OutputDevice, 0, ctypes.sizeof(output_device), ctypes.byref(output_device)
        )
        if result != EDS_OK and self.debug:
            print(f"[CanonCamera DEBUG] Evf_OutputDevice error: {hex(result)}")

        # Zkusit Movie mód (není nutný pro všechny modely)
        record_state = ctypes.c_int(kEdsRecord_Start)
        err = self.edsdk.EdsSetPropertyData(
            self.cam_ref, kEdsPropID_Record, 0, ctypes.sizeof(record_state), ctypes.byref(record_state)
        )
        if err != EDS_OK and self.debug:
            print(f"[CanonCamera DEBUG] Movie mode start error: {hex(err)}")

        time.sleep(1.0)
        print("[CanonCamera] ✅ LiveView běží.")

    def get_frame(self):
        """Získá aktuální LiveView snímek z kamery."""
        if not self.available or not self.initialized:
            return None

        for attempt in range(3):
            try:
                stream_ref = ctypes.c_void_p()
                evf_image = ctypes.c_void_p()

                self.edsdk.EdsCreateMemoryStream(0, ctypes.byref(stream_ref))
                self.edsdk.EdsCreateEvfImageRef(stream_ref, ctypes.byref(evf_image))

                err = self.edsdk.EdsDownloadEvfImage(self.cam_ref, evf_image)
                if err != EDS_OK:
                    if self.debug:
                        print(f"[CanonCamera DEBUG] EvfDownload error {hex(err)}, retry {attempt+1}/3")
                    time.sleep(0.3)
                    continue

                pointer = ctypes.c_void_p()
                size = ctypes.c_uint64()
                self.edsdk.EdsGetPointer(stream_ref, ctypes.byref(pointer))
                self.edsdk.EdsGetLength(stream_ref, ctypes.byref(size))

                if size.value == 0:
                    time.sleep(0.2)
                    continue

                # Dekódování JPEG streamu
                data = (ctypes.c_ubyte * size.value).from_address(pointer.value)
                img_array = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                # Uvolnit referenční objekty
                self.edsdk.EdsRelease(evf_image)
                self.edsdk.EdsRelease(stream_ref)

                if frame is not None:
                    return frame

            except Exception as e:
                if self.debug:
                    print(f"[CanonCamera DEBUG] get_frame exception: {e}")
                time.sleep(0.3)

        return None

    def stop_liveview(self):
        """Zastaví LiveView a Movie režim."""
        if not self.initialized:
            return

        try:
            record_state = ctypes.c_int(kEdsRecord_Stop)
            self.edsdk.EdsSetPropertyData(
                self.cam_ref, kEdsPropID_Record, 0, ctypes.sizeof(record_state), ctypes.byref(record_state)
            )
        except Exception:
            pass

        time.sleep(0.3)

    def close(self):
        """Ukončí relaci a EDSDK."""
        if not self.initialized:
            return

        try:
            self.edsdk.EdsCloseSession(self.cam_ref)
        except Exception:
            pass

        try:
            self.edsdk.EdsTerminateSDK()
            print("[CanonCamera] ✅ SDK ukončeno.")
        except Exception:
            pass

    def _check(self, err, action=""):
        """Kontrola návratového kódu EDSDK."""
        if err != EDS_OK:
            raise RuntimeError(f"[CanonCamera] Chyba {hex(err)} při {action}")

    def stop(self):
        """Ukončí LiveView a zavře SDK session."""
        try:
            if self.camera is not None:
                # Pokus o zastavení LiveView
                if self.sdk is not None:
                    try:
                        self.sdk.EdsSendCommand(self.camera, 0x00000001, 0)  # kód pro ukončení LiveView
                        print("[CanonCamera] 📴 LiveView zastaven.")
                    except Exception:
                        pass

                # Zavři session
                self.sdk.EdsCloseSession(self.camera)
                print("[CanonCamera] ❎ Session uzavřena.")

            # Ukonči SDK
            if self.sdk is not None:
                self.sdk.EdsTerminateSDK()
                print("[CanonCamera] ✅ SDK ukončeno.")

        except Exception as e:
            print(f"[CanonCamera] ⚠️ Chyba při ukončování: {e}")
