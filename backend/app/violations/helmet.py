"""
Helmet Non-Compliance — the flagship, fully-implemented module.

CUSTOM MODE: the fine-tuned model emits helmet / no_helmet boxes
directly over each rider's head. We just match them to riders.

FALLBACK MODE (no trained weights yet): we produce a real result using
two classical-CV signals on the head region of every motorcycle rider:
  1. Texture/uniformity — a helmet shell is a smooth, low-variance blob;
     bare hair has much higher local intensity variance.
  2. Skin-tone exposure — if a meaningful fraction of the head region
     falls in HSV skin-tone range (forehead/face visible), that's strong
     evidence of no helmet.
This is a deliberately transparent heuristic, not a trained classifier —
it's what your fine-tuned weights replace for production-grade accuracy.
Swap-in is automatic (see detection/detector.py).
"""
from __future__ import annotations

from typing import List

import cv2
import numpy as np

from app.violations.base import ViolationModule, ViolationResult
from app.detection.detector import Detection, get_detector
from app.utils.image_utils import riders_on_motorcycle, head_region


def _heuristic_no_helmet_score(image: np.ndarray, person: Detection) -> float:
    x1, y1, x2, y2 = head_region(person)
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
    if x2 <= x1 or y2 <= y1:
        return 0.5

    crop = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    texture_var = float(np.var(gray))
    texture_score = min(texture_var / 1200.0, 1.0)

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 30, 60], dtype=np.uint8)
    upper = np.array([25, 180, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv, lower, upper)
    skin_ratio = float(np.mean(skin_mask > 0))

    score = 0.55 * skin_ratio + 0.45 * texture_score
    return float(np.clip(score, 0.0, 1.0))


class HelmetModule(ViolationModule):
    name = "helmet_non_compliance"
    label = "Helmet Non Compliance"
    implemented = True

    def evaluate(self, image: np.ndarray, detections: List[Detection]) -> List[ViolationResult]:
        detector = get_detector()
        results: List[ViolationResult] = []

        motorcycles = [d for d in detections if d.label == "motorcycle"]
        persons = [d for d in detections if d.label == "person"]

        if detector.is_custom():
            helmets = [d for d in detections if d.label == "helmet"]
            no_helmets = [d for d in detections if d.label == "no_helmet"]
            for moto in motorcycles:
                riders = riders_on_motorcycle(moto, persons)
                for rider in riders:
                    rx1, ry1, rx2, ry2 = head_region(rider)
                    nh = _best_overlap(no_helmets, rx1, ry1, rx2, ry2)
                    hh = _best_overlap(helmets, rx1, ry1, rx2, ry2)
                    if nh and (not hh or nh.confidence >= hh.confidence):
                        results.append(
                            ViolationResult(
                                violation_type=self.name,
                                violation_label="Helmet Missing",
                                confidence=nh.confidence,
                                vehicle_type="Motorcycle",
                                extra_boxes=[nh],
                            )
                        )
        else:
            for moto in motorcycles:
                riders = riders_on_motorcycle(moto, persons)
                for rider in riders:
                    score = _heuristic_no_helmet_score(image, rider)
                    if score >= 0.5:
                        x1, y1, x2, y2 = head_region(rider)
                        flagged = Detection("no_helmet", score, x1, y1, x2, y2, -1)
                        results.append(
                            ViolationResult(
                                violation_type=self.name,
                                violation_label="Helmet Missing",
                                confidence=round(score, 3),
                                vehicle_type="Motorcycle",
                                extra_boxes=[flagged],
                            )
                        )
        return results


def _best_overlap(boxes: List[Detection], x1, y1, x2, y2):
    best, best_iou = None, 0.0
    for b in boxes:
        ix1, iy1 = max(b.x1, x1), max(b.y1, y1)
        ix2, iy2 = min(b.x2, x2), min(b.y2, y2)
        if ix2 <= ix1 or iy2 <= iy1:
            continue
        inter = (ix2 - ix1) * (iy2 - iy1)
        area_b = (b.x2 - b.x1) * (b.y2 - b.y1)
        if area_b <= 0:
            continue
        iou = inter / area_b
        if iou > best_iou:
            best_iou, best = iou, b
    return best if best_iou > 0.15 else None
