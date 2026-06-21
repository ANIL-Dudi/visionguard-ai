from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import ViolationRecord

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


def _get_or_404(db: Session, violation_id: str) -> ViolationRecord:
    record = db.query(ViolationRecord).filter(ViolationRecord.id == violation_id).first()
    if not record:
        raise HTTPException(404, f"Violation {violation_id} not found.")
    return record


@router.get("/{violation_id}/image")
def get_annotated_image(violation_id: str, db: Session = Depends(get_db)):
    record = _get_or_404(db, violation_id)
    return FileResponse(record.annotated_image_path, media_type="image/jpeg")


@router.get("/{violation_id}/card")
def get_evidence_card(violation_id: str, db: Session = Depends(get_db)):
    record = _get_or_404(db, violation_id)
    if not record.evidence_card_path:
        raise HTTPException(404, "Evidence card not generated for this record.")
    return FileResponse(record.evidence_card_path, media_type="image/png")


@router.get("/{violation_id}")
def get_evidence_json(violation_id: str, db: Session = Depends(get_db)):
    record = _get_or_404(db, violation_id)
    return {
        "id": record.id,
        "created_at": record.created_at.isoformat(),
        "vehicle_type": record.vehicle_type,
        "violation_type": record.violation_type,
        "violation_label": record.violation_label,
        "confidence": record.confidence,
        "plate_text": record.plate_text,
        "plate_confidence": record.plate_confidence,
        "rider_count": record.rider_count,
        "risk_score": record.risk_score,
        "risk_level": record.risk_level,
        "recommendation": record.recommendation,
        "is_repeat_offender": bool(record.is_repeat_offender),
        "annotated_image_url": f"/api/evidence/{record.id}/image",
        "evidence_card_url": f"/api/evidence/{record.id}/card",
    }
