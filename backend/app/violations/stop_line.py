"""
Stop Line Violation — architecture module (not yet active).
Simplest unimplemented module to bring online: once a stop-line ROI is
calibrated per camera, this becomes a pure geometry check across
multiple frames. No new model training required.
"""
from typing import List
from app.violations.base import ViolationModule, ViolationResult, NotImplementedYet
from app.detection.detector import Detection


class StopLineModule(ViolationModule):
    name = "stop_line_violation"
    label = "Stop Line Violation"
    implemented = False

    def evaluate(self, image, detections: List[Detection]) -> List[ViolationResult]:
        raise NotImplementedYet(
            self.label,
            "Needs a one-time calibrated stop-line ROI per camera and "
            "multi-frame input to confirm the vehicle was stationary "
            "across the line.",
        )
