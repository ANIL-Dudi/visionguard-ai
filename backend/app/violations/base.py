"""
Every violation type plugs into the engine through this one interface.
Helmet and Triple Riding implement evaluate() fully; Seatbelt, Wrong
Side, Red Light, Stop Line and Illegal Parking are wired into the
registry and raise NotImplementedYet with a clear note on what input
each one needs — so adding them later is a matter of writing one
evaluate() method, not redesigning anything.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from app.detection.detector import Detection


class NotImplementedYet(Exception):
    def __init__(self, module_name: str, requirement_note: str):
        self.module_name = module_name
        self.requirement_note = requirement_note
        super().__init__(f"{module_name}: {requirement_note}")


@dataclass
class ViolationResult:
    violation_type: str
    violation_label: str
    confidence: float
    vehicle_type: str
    rider_count: Optional[int] = None
    extra_boxes: List[Detection] = field(default_factory=list)


class ViolationModule(ABC):
    name: str
    label: str
    implemented: bool = False

    @abstractmethod
    def evaluate(self, image, detections: List[Detection]) -> List[ViolationResult]:
        raise NotImplementedError
