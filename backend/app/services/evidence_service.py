"""
Evidence Service — owns Screen 4 (Evidence Card):
  - sequential violation IDs (V0001, V0002, ...)
  - saving the annotated (bounding-boxed) image to disk
  - rendering a clean, printable evidence card PNG bundling vehicle
    type, violation, plate, timestamp and the annotated photo.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app.config import settings
from app.models_db import ViolationRecord


def next_violation_id(db: Session) -> str:
    count = db.query(ViolationRecord).count() + 1
    return f"V{count:04d}"


def save_annotated_image(annotated_bgr: np.ndarray, violation_id: str) -> str:
    path = settings.EVIDENCE_DIR / f"{violation_id}_annotated.jpg"
    cv2.imwrite(str(path), annotated_bgr)
    return str(path)


def _load_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def render_evidence_card(
    violation_id: str,
    vehicle_type: str,
    violation_label: str,
    plate_text,
    annotated_image_path: str,
    timestamp: dt.datetime,
) -> str:
    photo = Image.open(annotated_image_path).convert("RGB")
    photo.thumbnail((640, 480))

    card_w = max(640, photo.width)
    card_h = photo.height + 230
    card = Image.new("RGB", (card_w, card_h), (22, 27, 34))
    draw = ImageDraw.Draw(card)

    photo_x = (card_w - photo.width) // 2
    card.paste(photo, (photo_x, 16))

    title_font = _load_font(22)
    label_font = _load_font(15)
    value_font = _load_font(18)

    y = photo.height + 32
    draw.text((20, y), "VISIONGUARD AI — VIOLATION EVIDENCE", font=title_font, fill=(45, 212, 191))
    y += 34

    rows = [
        ("VIOLATION ID", violation_id),
        ("VEHICLE", vehicle_type),
        ("VIOLATION", violation_label),
        ("PLATE", plate_text or "UNREADABLE"),
        ("TIME", timestamp.strftime("%d-%b-%Y %H:%M")),
    ]
    col_w = card_w // 2
    for i, (k, v) in enumerate(rows):
        cx = 20 + (i % 2) * col_w
        cy = y + (i // 2) * 46
        draw.text((cx, cy), k, font=label_font, fill=(139, 148, 158))
        draw.text((cx, cy + 18), str(v), font=value_font, fill=(230, 237, 243))

    out_path = settings.EVIDENCE_DIR / f"{violation_id}_card.png"
    card.save(out_path)
    return str(out_path)
