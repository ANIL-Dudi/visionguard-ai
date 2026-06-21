from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import ViolationRecord
from app.schemas import ViolationOut

router = APIRouter(prefix="/api/violations", tags=["violations"])


@router.get("", response_model=list[ViolationOut])
def list_violations(
    db: Session = Depends(get_db),
    limit: int = Query(50, le=500),
    violation_type: str | None = None,
    plate_text: str | None = None,
):
    q = db.query(ViolationRecord)
    if violation_type:
        q = q.filter(ViolationRecord.violation_type == violation_type)
    if plate_text:
        q = q.filter(ViolationRecord.plate_text == plate_text)
    rows = q.order_by(ViolationRecord.created_at.desc()).limit(limit).all()
    return [
        ViolationOut(
            id=r.id,
            created_at=r.created_at.isoformat(),
            vehicle_type=r.vehicle_type,
            violation_type=r.violation_type,
            violation_label=r.violation_label,
            confidence=r.confidence,
            plate_text=r.plate_text,
            risk_score=r.risk_score,
            risk_level=r.risk_level,
            recommendation=r.recommendation,
            annotated_image_url=f"/api/evidence/{r.id}/image",
        )
        for r in rows
    ]
