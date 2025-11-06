# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 10:04:30 2025

@author: Milan
"""

import os
import time
import ctypes
import numpy as np
import cv2

EDS_OK = 0x00000000
kEdsPropID_Evf_OutputDevice = 0x00000500
kEdsEvfOutputDevice_PC = 0x00000002
kEdsPropID_Record = 0x00000501
kEdsRecord_Stop = 0
kEdsRecord_Start = 4

kEdsPropID_Tv = 0x0000040E
kEdsPropID_Av = 0x0000040D
kEdsPropID_ISOSpeed = 0x0000040F
kEdsPropID_AEMode = 0x00000400
kEdsPropID_WhiteBalance = 0x00000407
kEdsPropID_ExposureComp = 0x00000406

kEdsAEMode_Manual = 0x13
kEdsWhiteBalance_Daylight = 0x02


class CanonCamera:
    """Canon EOS LiveView kamera pro GUI (PyQt6) – stabilní inicializace."""

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
            print(f"[CanonCamera] Loaded EDSDK from: {sdk_path}")
            self.available = True
        except Exception as e:
            raise RuntimeError(f"[CanonCamera] Nelze načíst EDSDK DLL: {e}")

    def initialize(self):
        """Inicializuje EDSDK a otevře relaci s kamerou."""
        if not self.available:
            raise RuntimeError("[CanonCamera] SDK není k dispozici")

        print("[CanonCamera] ⏳ Inicializuji EDSDK...")
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

        # krátká prodleva – Canon SDK to vyžaduje
        time.sleep(1.0)

        # Nastavení expozice
        self._apply_default_settings()

    def _apply_default_settings(self):
        """Stejná expozice jako ve funkční CLI verzi."""
        try:
            print("[CanonCamera] ⚙️ Nastavuji expoziční parametry pro LiveView...")

            self._set_property(kEdsPropID_AEMode, 0x03)  # Program AE
            self._set_property(kEdsPropID_ISOSpeed, 0x00)  # Auto ISO
            self._set_property(kEdsPropID_ExposureComp, 0x10)  # -1 EV
            self._set_property(kEdsPropID_WhiteBalance, 0x00)  # Auto WB
            self._set_property(kEdsPropID_Evf_OutputDevice, kEdsEvfOutputDevice_PC)

            print("[CanonCamera] ✅ Parametry nastaveny (P, Auto ISO, -1EV, Auto WB).")

        except Exception as e:
            print(f"[CanonCamera] ⚠️ Chyba při nastavování parametrů: {e}")

    def _set_property(self, prop_id, value):
        val = ctypes.c_int(value)
        err = self.edsdk.EdsSetPropertyData(self.cam_ref, prop_id, 0, ctypes.sizeof(val), ctypes.byref(val))
        if err != EDS_OK and self.debug:
            print(f"[CanonCamera DEBUG] Chyba {hex(err)} při nastavování property {hex(prop_id)}")

    def start_liveview(self):
        """Bezpečně spustí LiveView – s retry logikou."""
        if not self.initialized:
            raise RuntimeError("[CanonCamera] Nelze spustit LiveView – kamera není inicializována.")

        for attempt in range(3):
            output_device = ctypes.c_int(kEdsEvfOutputDevice_PC)
            result = self.edsdk.EdsSetPropertyData(
                self.cam_ref, kEdsPropID_Evf_OutputDevice, 0, ctypes.sizeof(output_device), ctypes.byref(output_device)
            )

            record_state = ctypes.c_int(kEdsRecord_Start)
            err = self.edsdk.EdsSetPropertyData(
                self.cam_ref, kEdsPropID_Record, 0, ctypes.sizeof(record_state), ctypes.byref(record_state)
            )

            if result == EDS_OK and err == EDS_OK:
                print("[CanonCamera] ✅ LiveView běží.")
                return
            else:
                print(f"[CanonCamera DEBUG] DoEvfStart error {hex(err)} (pok. {attempt+1}/3)")
                time.sleep(1.0)

        raise RuntimeError("[CanonCamera] ❌ LiveView se nepodařilo spustit po 3 pokusech.")

    def get_frame(self):
        """Načte aktuální snímek z LiveView."""
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
        """Zastaví LiveView."""
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
        """Uzavře session a SDK."""
        try:
            if self.cam_ref:
                self.edsdk.EdsCloseSession(self.cam_ref)
                print("[CanonCamera] ❎ Session uzavřena.")
            self.edsdk.EdsTerminateSDK()
            print("[CanonCamera] ✅ SDK ukončeno.")
        except Exception as e:
            print(f"[CanonCamera] ⚠️ Chyba při ukončování: {e}")

    def _check(self, err, action=""):
        if err != EDS_OK:
            raise RuntimeError(f"[CanonCamera] Chyba {hex(err)} při {action}")

    def stop(self):
        """Alias pro kompatibilitu – ukončí relaci a SDK."""
        self.close()