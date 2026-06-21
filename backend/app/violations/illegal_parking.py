"""
Illegal Parking — architecture module (not yet active).
Needs a no-parking-zone ROI per camera plus a dwell-time check. Reuses
the same motorcycle/car/truck detections already produced by the core
detector — no new detection class needed.
"""
from typing import List
from app.violations.base import ViolationModule, ViolationResult, NotImplementedYet
from app.detection.detector import Detection


class IllegalParkingModule(ViolationModule):
    name = "illegal_parking"
    label = "Illegal Parking"
    implemented = False

    def evaluate(self, image, detections: List[Detection]) -> List[ViolationResult]:
        raise NotImplementedYet(
            self.label,
            "Needs a no-parking-zone ROI per camera and a dwell-time check "
            "across multiple frames over time — not derivable from one image.",
        )
