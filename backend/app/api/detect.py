from __future__ import annotations

import datetime as dt
import logging

import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import ViolationRecord
from app.detection.detector import get_detector
from app.detection.plate_ocr import read_plate
from app.violations.engine import get_engine
from app.services import risk_engine, recommendation_engine, evidence_service
from app.schemas import DetectionResponse, BoundingBox, PlateResult, RiskResult
from app.utils.image_utils import crop_box, draw_annotations

logger = logging.getLogger("visionguard.api.detect")
router = APIRouter(prefix="/api", tags=["detect"])

VEHICLE_LABELS = {"motorcycle", "car", "bus", "truck"}


@router.post("/detect", response_model=DetectionResponse)
async def detect(image: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = await image.read()
    np_arr = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(400, "Could not decode image. Please upload a JPG/PNG.")

    detector = get_detector()
    detections = detector.predict(frame)

    engine = get_engine()
    violations = engine.run(frame, detections)

    if not violations:
        raise HTTPException(
            422,
            "No violation detected in this image. (Detections seen: "
            f"{[d.label for d in detections]})",
        )

    primary = max(violations, key=lambda v: v.confidence)

    vehicles = [d for d in detections if d.label in VEHICLE_LABELS]
    plate_text, plate_conf, plate_valid = None, None, False
    if vehicles:
        best_vehicle = max(vehicles, key=lambda d: d.confidence)
        vehicle_crop = crop_box(frame, best_vehicle, pad=0.08)
        plate_text, plate_conf, plate_valid = read_plate(vehicle_crop)

    prior_count = 0
    if plate_text:
        prior_count = (
            db.query(ViolationRecord).filter(ViolationRecord.plate_text == plate_text).count()
        )

    risk = risk_engine.compute_risk(
        primary.violation_type, primary.confidence, prior_violation_count=prior_count
    )
    recommendation = recommendation_engine.recommend(
        primary.violation_type,
        risk["level"],
        plate_text,
        plate_valid,
        primary.confidence,
        risk["is_repeat_offender"],
    )

    boxes = []
    for d in detections:
        boxes.append(BoundingBox(label=d.label, confidence=d.confidence, x1=d.x1, y1=d.y1, x2=d.x2, y2=d.y2, kind="detection"))
    for v in violations:
        for b in v.extra_boxes:
            kind = "critical" if risk["level"] in ("High", "Critical") else "violation"
            boxes.append(BoundingBox(label=b.label, confidence=b.confidence, x1=b.x1, y1=b.y1, x2=b.x2, y2=b.y2, kind=kind))

    annotated = draw_annotations(frame, [b.model_dump() for b in boxes])

    violation_id = evidence_service.next_violation_id(db)
    annotated_path = evidence_service.save_annotated_image(annotated, violation_id)
    now = dt.datetime.utcnow()
    card_path = evidence_service.render_evidence_card(
        violation_id, primary.vehicle_type, primary.violation_label, plate_text, annotated_path, now
    )

    record = ViolationRecord(
        id=violation_id,
        created_at=now,
        image_path=annotated_path,
        annotated_image_path=annotated_path,
        evidence_card_path=card_path,
        vehicle_type=primary.vehicle_type,
        violation_type=primary.violation_type,
        violation_label=primary.violation_label,
        confidence=primary.confidence,
        plate_text=plate_text,
        plate_confidence=plate_conf,
        rider_count=primary.rider_count,
        risk_score=risk["score"],
        risk_level=risk["level"],
        recommendation=recommendation,
        is_repeat_offender=1 if risk["is_repeat_offender"] else 0,
        detections_json=[b.model_dump() for b in boxes],
    )
    db.add(record)
    db.commit()

    return DetectionResponse(
        violation_id=violation_id,
        vehicle_type=primary.vehicle_type,
        violation_type=primary.violation_type,
        violation_label=primary.violation_label,
        confidence=primary.confidence,
        rider_count=primary.rider_count,
        boxes=boxes,
        plate=PlateResult(text=plate_text, confidence=plate_conf, valid_format=plate_valid),
        risk=RiskResult(**risk),
        recommendation=recommendation,
        annotated_image_url=f"/api/evidence/{violation_id}/image",
        timestamp=now.isoformat(),
    )
