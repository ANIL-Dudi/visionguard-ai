"""
Red Light Violation — architecture module (not yet active).
Needs (a) a signal-state feed or trained traffic-light-color classifier,
and (b) a calibrated stop-line ROI so "crossed while red" can be
evaluated geometrically.
"""
from typing import List
from app.violations.base import ViolationModule, ViolationResult, NotImplementedYet
from app.detection.detector import Detection


class RedLightModule(ViolationModule):
    name = "red_light_violation"
    label = "Red Light Violation"
    implemented = False

    def evaluate(self, image, detections: List[Detection]) -> List[ViolationResult]:
        raise NotImplementedYet(
            self.label,
            "Needs a live signal-state feed (or in-frame light-color "
            "classifier) plus a calibrated stop-line ROI per camera.",
        )
