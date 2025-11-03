# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 23:33:58 2025

@author: Milan
"""

# -*- coding: utf-8 -*-
"""
Test: ověření funkce CanonCamera.get_frame()
Zobrazí výstup z kamery v reálném čase (nebo mock)
"""

import time
import cv2
import numpy as np
from camera.camera_canon_G import CanonCamera


def main():
    sdk_path = r"C:\Users\Milan\Projekty\Cuda\EDSDKv131910W\Windows\EDSDK_64\Dll\EDSDK.dll"

    print("=== TEST: CanonCamera LiveView ===")
    cam = CanonCamera(sdk_path, debug=True)

    try:
        cam.initialize()
        cam.start_liveview()

        last_time = time.time()
        frame_count = 0

        while True:
            frame = cam.get_frame()
            if frame is None:
                print("[TEST] ⚠️ get_frame() → None")
                time.sleep(0.2)
                continue

            # počítání FPS
            frame_count += 1
            if frame_count % 10 == 0:
                now = time.time()
                fps = 10 / (now - last_time)
                last_time = now
                print(f"[TEST] FPS: {fps:.1f}, shape={frame.shape}")

            cv2.imshow("Canon LiveView (Test)", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break

        cam.stop_liveview()
        cam.stop()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"[TEST] ❌ Chyba: {e}")
        cam.stop()


if __name__ == "__main__":
    main()
