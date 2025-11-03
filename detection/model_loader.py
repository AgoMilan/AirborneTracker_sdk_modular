# detection/model_loader.py
import os
import sys
import ctypes

# --- Fix WinError 1114 při načítání Torch + CUDA ---
# Zajistí, že CUDA DLL se načtou dřív, než se importuje torch

def _add_cuda_paths():
    cuda_paths = [
        os.environ.get("CUDA_PATH"),
        os.environ.get("CUDA_PATH_V12_8"),
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8",
        r"C:\Windows\System32",
        os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib"),
    ]
    for path in cuda_paths:
        if path and os.path.exists(path):
            try:
                os.add_dll_directory(path)
            except Exception:
                pass

_add_cuda_paths()
# ----------------------------------------------------
import torch
from ultralytics import YOLO


from utils.logger import Logger

class ModelLoader:
    @staticmethod
    def load_model(model_path):
        logger = Logger(log_to_console=True)
        logger.info(f"Načítám YOLO model z: {model_path}")

        # Pokus o import torch – pokud selže, přepneme na CPU
        try:
            import torch
            from ultralytics import YOLO
            model = YOLO(model_path)

            try:
                if torch.cuda.is_available():
                    device = "cuda"
                    logger.info("✅ CUDA detekována – model poběží na GPU")
                else:
                    device = "cpu"
                    logger.warning("⚠️ CUDA není dostupná – model poběží na CPU")

                model.to(device)
                logger.info(f"Model běží na zařízení: {device.upper()}")
            except Exception as e:
                logger.warning(f"⚠️ CUDA selhala ({e}) – přepínám na CPU")
                model.to("cpu")

            return model

        except Exception as e:
            logger.warning(f"⚠️ PyTorch nelze inicializovat ({e}) – režim CPU-only")
            try:
                # Načteme YOLO jen s CPU (bez torch importu)
                from ultralytics import YOLO
                model = YOLO(model_path)
                logger.info("✅ Model načten v CPU-only režimu.")
                return model
            except Exception as e2:
                logger.error(f"❌ Model se nepodařilo načíst ani v CPU režimu: {e2}")
                raise e2
