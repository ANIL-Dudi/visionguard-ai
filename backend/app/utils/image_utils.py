from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np

from app.detection.detector import Detection

BOX_COLORS = {
    "detection": (45, 212, 191),
    "violation": (245, 166, 35),
    "critical": (239, 68, 68),
}


def crop_box(image: np.ndarray, det: Detection, pad: float = 0.0) -> np.ndarray:
    h_img, w_img = image.shape[:2]
    pw, ph = det.width * pad, det.height * pad
    x1 = max(0, int(det.x1 - pw))
    y1 = max(0, int(det.y1 - ph))
    x2 = min(w_img, int(det.x2 + pw))
    y2 = min(h_img, int(det.y2 + ph))
    return image[y1:y2, x1:x2]


def head_region(person: Detection) -> Tuple[int, int, int, int]:
    h = person.height
    x1, y1 = person.x1, person.y1
    x2 = person.x2
    y2 = person.y1 + 0.28 * h
    return int(x1), int(y1), int(x2), int(y2)


def riders_on_motorcycle(
    motorcycle: Detection, persons: List[Detection], iou_thresh: float = 0.0
) -> List[Detection]:
    riders = []
    widen = motorcycle.width * 0.25
    mx1, mx2 = motorcycle.x1 - widen, motorcycle.x2 + widen
    for p in persons:
        pcx, _ = p.center
        vertical_overlap = not (p.y2 < motorcycle.y1 - motorcycle.height * 0.3 or p.y1 > motorcycle.y2)
        if mx1 <= pcx <= mx2 and vertical_overlap:
            riders.append(p)
    riders.sort(key=lambda d: d.center[0])
    return riders


def draw_annotations(image: np.ndarray, boxes: List[dict]) -> np.ndarray:
    annotated = image.copy()
    for b in boxes:
        color = BOX_COLORS.get(b.get("kind", "detection"), BOX_COLORS["detection"])
        x1, y1, x2, y2 = int(b["x1"]), int(b["y1"]), int(b["x2"]), int(b["y2"])
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        text = f'{b["label"]} {b["confidence"]:.0%}'
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x1, max(0, y1 - th - 8)), (x1 + tw + 6, y1), color, -1)
        cv2.putText(
            annotated, text, (x1 + 3, max(12, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (15, 15, 15), 1, cv2.LINE_AA,
        )
    return annotated
