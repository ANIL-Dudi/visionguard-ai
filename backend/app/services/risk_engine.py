"""
Risk Engine — turns a raw violation + context into a 0-100 score and a
band (Low/Medium/High/Critical), matching the "Helmet = Medium Risk,
Score = 25" panel in the spec, generalized to every violation type.

score = base_score(violation_type)
        + repeat_offender_bonus * prior_violation_count_for_plate
        + confidence_penalty (if detection confidence is low)
"""
from __future__ import annotations

from app.config import settings


def band_for_score(score: int) -> str:
    for lo, hi, label in settings.RISK_BANDS:
        if lo <= score < hi:
            return label
    return settings.RISK_BANDS[-1][2]


def compute_risk(
    violation_type: str,
    confidence: float,
    prior_violation_count: int = 0,
) -> dict:
    base = settings.RISK_BASE_SCORE.get(violation_type, 20)
    repeat_bonus = settings.RISK_REPEAT_OFFENDER_BONUS * prior_violation_count
    conf_penalty = settings.RISK_LOW_CONFIDENCE_PENALTY if confidence < 0.6 else 0

    raw_score = base + repeat_bonus + conf_penalty
    score = max(0, min(100, raw_score))

    return {
        "score": int(score),
        "level": band_for_score(score),
        "base_score": base,
        "repeat_offender_bonus": repeat_bonus,
        "confidence_penalty": conf_penalty,
        "is_repeat_offender": prior_violation_count > 0,
    }
