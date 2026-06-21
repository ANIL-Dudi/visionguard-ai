"""
Number Plate Recognition (ANPR-lite).

Pipeline:
  1. Crop the region under the vehicle bounding box.
  2. Classical CV plate localization: grayscale -> bilateral filter ->
     Canny edges -> contour search for a rectangular, plate-shaped blob
     (aspect ratio ~2:1 to 5:1). Works even in fallback mode.
  3. EasyOCR reads the localized crop, falling back to the full vehicle
     crop if localization fails.
  4. Text is cleaned (uppercase, strip non-alphanumerics) and validated
     against the Indian plate regex.
"""
from __future__ import annotations

import re
import logging
from typing import Optional, Tuple

import cv2
import numpy as np

from app.config import settings

logger = logging.getLogger("visionguard.ocr")

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr

        logger.info("Loading EasyOCR reader (langs=%s)...", settings.OCR_LANGS)
        _reader = easyocr.Reader(settings.OCR_LANGS, gpu=False)
    return _reader


def _locate_plate_crop(vehicle_crop: np.ndarray) -> Optional[np.ndarray]:
    if vehicle_crop.size == 0:
        return None
    gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edges = cv2.Canny(gray, 30, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

    h_img, w_img = gray.shape
    best = None
    best_score = -1
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if h == 0 or w == 0:
            continue
        aspect = w / h
        area_ratio = (w * h) / (w_img * h_img)
        if 1.8 <= aspect <= 5.5 and 0.01 <= area_ratio <= 0.35 and y > h_img * 0.25:
            score = area_ratio
            if score > best_score:
                best_score = score
                best = (x, y, w, h)

    if best is None:
        return None
    x, y, w, h = best
    pad = 4
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(w_img, x + w + pad), min(h_img, y + h + pad)
    return vehicle_crop[y0:y1, x0:x1]


def _clean_plate_text(raw: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]", "", raw).upper()
    text = text.replace("IND", "")
    return text


def read_plate(vehicle_crop: np.ndarray) -> Tuple[Optional[str], Optional[float], bool]:
    """Returns (text, confidence, looks_like_valid_plate)."""
    if vehicle_crop is None or vehicle_crop.size == 0:
        return None, None, False

    crop = _locate_plate_crop(vehicle_crop)
    candidates = [crop, vehicle_crop] if crop is not None else [vehicle_crop]

    reader = _get_reader()
    best_text, best_conf = None, 0.0

    for cand in candidates:
        if cand is None or cand.size == 0:
            continue
        try:
            results = reader.readtext(cand)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("EasyOCR failed on candidate: %s", exc)
            continue
        for _, text, conf in results:
            cleaned = _clean_plate_text(text)
            if len(cleaned) >= 6 and conf > best_conf:
                best_text, best_conf = cleaned, conf
        if best_text:
            break

    if not best_text:
        return None, None, False

    valid = bool(re.match(settings.PLATE_REGEX, best_text))
    return best_text, round(float(best_conf), 3), valid
