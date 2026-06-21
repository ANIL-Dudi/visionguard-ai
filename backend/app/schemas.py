from typing import List, Optional
from pydantic import BaseModel


class BoundingBox(BaseModel):
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    kind: str = "detection"


class PlateResult(BaseModel):
    text: Optional[str] = None
    confidence: Optional[float] = None
    valid_format: bool = False


class RiskResult(BaseModel):
    score: int
    level: str
    base_score: int
    repeat_offender_bonus: int
    confidence_penalty: int
    is_repeat_offender: bool


class DetectionResponse(BaseModel):
    violation_id: str
    vehicle_type: str
    violation_type: str
    violation_label: str
    confidence: float
    rider_count: Optional[int] = None
    boxes: List[BoundingBox]
    plate: PlateResult
    risk: RiskResult
    recommendation: str
    annotated_image_url: str
    timestamp: str


class ViolationOut(BaseModel):
    id: str
    created_at: str
    vehicle_type: str
    violation_type: str
    violation_label: str
    confidence: float
    plate_text: Optional[str]
    risk_score: int
    risk_level: str
    recommendation: str
    annotated_image_url: str

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_violations: int
    by_type: dict
    by_risk_level: dict
    avg_risk_score: float
    repeat_offender_count: int
    plates_flagged: int
    implemented_modules: List[str]
    architecture_modules: List[str]
