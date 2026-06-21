"""
Seatbelt Violation — architecture module (not yet trained/active).
Bringing it online needs:
  - A seatbelt/no_seatbelt class on car/truck cabin crops in the
    training dataset (windshield-region crop, similar to head_region()
    used by Helmet).
  - Front-facing camera angle (seatbelt is not visible from rear/side
    traffic-cam shots), so this also needs a camera-angle metadata tag.
"""
from typing import List
from app.violations.base import ViolationModule, ViolationResult, NotImplementedYet
from app.detection.detector import Detection


class SeatbeltModule(ViolationModule):
    name = "seatbelt_violation"
    label = "Seatbelt Violation"
    implemented = False

    def evaluate(self, image, detections: List[Detection]) -> List[ViolationResult]:
        raise NotImplementedYet(
            self.label,
            "Needs a seatbelt/no_seatbelt trained class on windshield-region "
            "crops, plus front-facing camera angle metadata.",
        )
