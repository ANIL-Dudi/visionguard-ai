"""
ViolationEngine — the registry that *is* the architecture diagram:

    Violation Engine
    ├── Helmet Module          [LIVE]
    ├── Triple Riding Module   [LIVE]
    ├── Seatbelt Module        [architecture]
    ├── Wrong Side Module      [architecture]
    ├── Red Light Module       [architecture]
    ├── Stop Line Module       [architecture]
    └── Illegal Parking Module [architecture]
"""
from __future__ import annotations

from typing import List

from app.detection.detector import Detection
from app.violations.base import ViolationModule, ViolationResult, NotImplementedYet
from app.violations.helmet import HelmetModule
from app.violations.triple_riding import TripleRidingModule
from app.violations.seatbelt import SeatbeltModule
from app.violations.wrong_side import WrongSideModule
from app.violations.red_light import RedLightModule
from app.violations.stop_line import StopLineModule
from app.violations.illegal_parking import IllegalParkingModule


class ViolationEngine:
    def __init__(self):
        self.modules: List[ViolationModule] = [
            HelmetModule(),
            TripleRidingModule(),
            SeatbeltModule(),
            WrongSideModule(),
            RedLightModule(),
            StopLineModule(),
            IllegalParkingModule(),
        ]

    def implemented_modules(self) -> List[str]:
        return [m.label for m in self.modules if m.implemented]

    def architecture_modules(self) -> List[str]:
        return [m.label for m in self.modules if not m.implemented]

    def run(self, image, detections: List[Detection]) -> List[ViolationResult]:
        all_results: List[ViolationResult] = []
        for module in self.modules:
            if not module.implemented:
                continue
            try:
                all_results.extend(module.evaluate(image, detections))
            except NotImplementedYet:
                continue
        return all_results


_engine = None


def get_engine() -> ViolationEngine:
    global _engine
    if _engine is None:
        _engine = ViolationEngine()
    return _engine
