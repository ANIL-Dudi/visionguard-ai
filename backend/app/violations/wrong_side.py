"""
Wrong Side Driving — architecture module (not yet active).
Needs a lane-direction reference per camera, then compares each
vehicle's frame-to-frame motion vector (requires multi-frame tracking)
against it. Structurally needs video/sequential frames rather than a
single uploaded image.
"""
from typing import List
from app.violations.base import ViolationModule, ViolationResult, NotImplementedYet
from app.detection.detector import Detection


class WrongSideModule(ViolationModule):
    name = "wrong_side_driving"
    label = "Wrong Side Driving"
    implemented = False

    def evaluate(self, image, detections: List[Detection]) -> List[ViolationResult]:
        raise NotImplementedYet(
            self.label,
            "Needs per-camera lane-direction calibration and multi-frame "
            "vehicle tracking (optical flow / Kalman tracker) to derive a "
            "motion vector — not available from a single still image.",
        )
