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

# Expoziční vlastnosti
kEdsPropID_Tv = 0x0000040E              # Čas závěrky
kEdsPropID_Av = 0x0000040D              # Clona
kEdsPropID_ISOSpeed = 0x0000040F        # ISO
kEdsPropID_AEMode = 0x00000400          # Expoziční režim
kEdsPropID_WhiteBalance = 0x00000407    # Vyvážení bílé
kEdsPropID_ExposureComp = 0x00000406    # Kompenzace expozice

# Hodnoty režimů
kEdsAEMode_Manual = 0x13
kEdsWhiteBalance_Daylight = 0x02


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

        try:
            self.edsdk.EdsRelease(cam_list)
        except Exception:
            pass

        self._check(self.edsdk.EdsOpenSession(cam_ref), "EdsOpenSession")
        self.cam_ref = cam_ref
        self.initialized = True
        print("[CanonCamera] ✅ Session otevřena.")

        # Nastavení expozice
        self._apply_default_settings()

    def _apply_default_settings(self):
        """Optimalizované nastavení pro Canon EOS 77D – korektní LiveView expozice."""
        try:
            print("[CanonCamera] ⚙️ Nastavuji expoziční parametry pro LiveView...")

            # ✅ Přepnout do režimu Program AE (automatická expozice)
            self._set_property(kEdsPropID_AEMode, 0x03)  # Program AE


            # ✅ ISO – Auto
            self._set_property(kEdsPropID_ISOSpeed, 0x00)

            # ✅ Kompenzace expozice: mírné ztmavení (-1 EV)
            self._set_property(kEdsPropID_ExposureComp, 0x10)

            # ✅ Vyvážení bílé: automatické
            self._set_property(kEdsPropID_WhiteBalance, 0x00)

            # ✅ Zapnout LiveView výstup na PC
            self._set_property(kEdsPropID_Evf_OutputDevice, kEdsEvfOutputDevice_PC)

            print("[CanonCamera] ✅ Parametry nastaveny (P, Auto ISO, -1EV, Auto WB, AE aktivní).")

        except Exception as e:
            print(f"[CanonCamera] ⚠️ Chyba při nastavování parametrů: {e}")


    def _set_property(self, prop_id, value):
        """Pomocná funkce pro nastavení parametru."""
        val = ctypes.c_int(value)
        err = self.edsdk.EdsSetPropertyData(self.cam_ref, prop_id, 0, ctypes.sizeof(val), ctypes.byref(val))
        if err != EDS_OK and self.debug:
            print(f"[CanonCamera DEBUG] Chyba {hex(err)} při nastavování property {hex(prop_id)}")

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

                data = (ctypes.c_ubyte * size.value).from_address(pointer.value)
                img_array = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

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
            if self.cam_ref is not None:
                self.stop_liveview()
                self.edsdk.EdsCloseSession(self.cam_ref)
                print("[CanonCamera] ❎ Session uzavřena.")

            if self.edsdk is not None:
                self.edsdk.EdsTerminateSDK()
                print("[CanonCamera] ✅ SDK ukončeno.")

        except Exception as e:
            print(f"[CanonCamera] ⚠️ Chyba při ukončování: {e}")
