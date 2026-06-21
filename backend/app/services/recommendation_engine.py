"""
Officer Recommendations — translates (violation, risk, plate, OCR
confidence) into a plain-language next action.
"""
from __future__ import annotations


def recommend(
    violation_type: str,
    risk_level: str,
    plate_text,
    plate_valid_format: bool,
    detection_confidence: float,
    is_repeat_offender: bool,
) -> str:
    if detection_confidence < 0.45:
        return "Low detection confidence — route to manual officer review before action."

    if not plate_text or not plate_valid_format:
        return "Violation confirmed but plate unreadable — flag for manual plate verification."

    if is_repeat_offender:
        return "Repeat offender on this plate — escalate to e-challan with repeat-offense surcharge."

    if risk_level == "Critical":
        return "Critical risk — issue e-challan immediately and flag for field interception."
    if risk_level == "High":
        return "High risk — issue e-challan and queue for supervisor review."
    if risk_level == "Medium":
        return "Issue standard e-challan."
    return "Low risk — log violation; e-challan optional per local policy."
