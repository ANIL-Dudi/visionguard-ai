"""
YOLOv8 detection wrapper.

Two operating modes, chosen automatically at startup:

1. CUSTOM MODE (backend/weights/helmet_triple_yolov8.pt exists)
   The model was fine-tuned on your own annotated dataset using
   backend/train/train_helmet.py, and emits the 5 classes defined in
   Settings.CUSTOM_CLASS_NAMES: motorcycle, person, helmet, no_helmet,
   number_plate. This is the accurate, "real" path.

2. FALLBACK MODE (no custom weights found)
   We load stock yolov8n.pt (general COCO classes) so the system still
   runs end-to-end out of the box. Helmet presence is then inferred with
   a rule-based heuristic over the head region of each detected person
   (see violations/helmet.py). The moment you drop trained weights into
   backend/weights/, mode 1 takes over with zero code changes.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import numpy as np
from ultralytics import YOLO

from app.config import settings

logger = logging.getLogger("visionguard.detector")


class Detection:
    __slots__ = ("label", "confidence", "x1", "y1", "x2", "y2", "cls_id")

    def __init__(self, label, confidence, x1, y1, x2, y2, cls_id):
        self.label = label
        self.confidence = confidence
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.cls_id = cls_id

    def as_dict(self, kind="detection"):
        return {
            "label": self.label,
            "confidence": round(float(self.confidence), 3),
            "x1": float(self.x1),
            "y1": float(self.y1),
            "x2": float(self.x2),
            "y2": float(self.y2),
            "kind": kind,
        }

    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1

    @property
    def center(self):
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2


class VehicleDetector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        custom_path = Path(settings.CUSTOM_WEIGHTS_PATH)
        if custom_path.exists():
            logger.info("Loading CUSTOM fine-tuned weights: %s", custom_path)
            self.model = YOLO(str(custom_path))
            self.mode = "custom"
            self.class_names = settings.CUSTOM_CLASS_NAMES
        else:
            logger.warning(
                "No custom weights at %s — falling back to pretrained '%s'. "
                "Train on your dataset with backend/train/train_helmet.py "
                "for full accuracy.",
                custom_path,
                settings.FALLBACK_WEIGHTS,
            )
            self.model = YOLO(settings.FALLBACK_WEIGHTS)
            self.mode = "fallback"
            self.class_names = None

    def predict(self, image: np.ndarray) -> List[Detection]:
        results = self.model.predict(
            image,
            conf=settings.DETECTION_CONFIDENCE_THRESHOLD,
            verbose=False,
        )[0]

        detections: List[Detection] = []
        names = results.names
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
            label = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else names[cls_id]
            detections.append(Detection(label, conf, x1, y1, x2, y2, cls_id))
        return detections

    def is_custom(self) -> bool:
        return self.mode == "custom"


def get_detector() -> VehicleDetector:
    return VehicleDetector()
