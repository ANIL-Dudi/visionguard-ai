"""
Triple Riding — fully implemented.

Counts persons associated with each detected motorcycle (see
utils.image_utils.riders_on_motorcycle) and flags when the count
reaches the configured threshold (default 3). Confidence is the mean
detection confidence across the motorcycle and its associated riders.
"""
from __future__ import annotations

from typing import List

import numpy as np

from app.config import settings
from app.violations.base import ViolationModule, ViolationResult
from app.detection.detector import Detection
from app.utils.image_utils import riders_on_motorcycle


class TripleRidingModule(ViolationModule):
    name = "triple_riding"
    label = "Triple Riding"
    implemented = True

    def evaluate(self, image, detections: List[Detection]) -> List[ViolationResult]:
        motorcycles = [d for d in detections if d.label == "motorcycle"]
        persons = [d for d in detections if d.label == "person"]
        results: List[ViolationResult] = []

        for moto in motorcycles:
            riders = riders_on_motorcycle(moto, persons)
            if len(riders) >= settings.TRIPLE_RIDING_MIN_RIDERS:
                confs = [moto.confidence] + [r.confidence for r in riders]
                results.append(
                    ViolationResult(
                        violation_type=self.name,
                        violation_label=f"Triple Riding ({len(riders)} riders)",
                        confidence=round(float(np.mean(confs)), 3),
                        vehicle_type="Motorcycle",
                        rider_count=len(riders),
                        extra_boxes=riders,
                    )
                )
        return results
