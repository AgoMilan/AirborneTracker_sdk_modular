# detection/model_loader.py
from ultralytics import YOLO

class ModelLoader:
    @staticmethod
    def load_model(model_path: str):
        print(f"[ModelLoader] Načítám YOLO model z: {model_path}")
        model = YOLO(model_path)
        return model

