from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models_db import ViolationRecord
from app.violations.engine import get_engine


def summary(db: Session) -> dict:
    total = db.query(ViolationRecord).count()

    by_type_rows = (
        db.query(ViolationRecord.violation_type, func.count(ViolationRecord.id))
        .group_by(ViolationRecord.violation_type)
        .all()
    )
    by_risk_rows = (
        db.query(ViolationRecord.risk_level, func.count(ViolationRecord.id))
        .group_by(ViolationRecord.risk_level)
        .all()
    )
    avg_risk = db.query(func.avg(ViolationRecord.risk_score)).scalar() or 0.0
    repeat_count = (
        db.query(ViolationRecord).filter(ViolationRecord.is_repeat_offender == 1).count()
    )
    plates_flagged = (
        db.query(func.count(func.distinct(ViolationRecord.plate_text)))
        .filter(ViolationRecord.plate_text.isnot(None))
        .scalar()
        or 0
    )

    engine = get_engine()

    return {
        "total_violations": total,
        "by_type": {k: v for k, v in by_type_rows},
        "by_risk_level": {k: v for k, v in by_risk_rows},
        "avg_risk_score": round(float(avg_risk), 1),
        "repeat_offender_count": repeat_count,
        "plates_flagged": plates_flagged,
        "implemented_modules": engine.implemented_modules(),
        "architecture_modules": engine.architecture_modules(),
    }
