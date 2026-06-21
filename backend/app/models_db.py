import datetime as dt

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON

from app.database import Base


class ViolationRecord(Base):
    __tablename__ = "violations"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    image_path = Column(String)
    annotated_image_path = Column(String)
    evidence_card_path = Column(String, nullable=True)

    vehicle_type = Column(String)
    violation_type = Column(String)
    violation_label = Column(String)
    confidence = Column(Float)

    plate_text = Column(String, nullable=True)
    plate_confidence = Column(Float, nullable=True)

    rider_count = Column(Integer, nullable=True)

    risk_score = Column(Integer)
    risk_level = Column(String)

    recommendation = Column(String)
    is_repeat_offender = Column(Integer, default=0)

    detections_json = Column(JSON)
