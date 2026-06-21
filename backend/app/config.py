"""
Central configuration for VisionGuard AI.
All tunables (model paths, thresholds, risk weights) live here so the
violation engine and detectors never hardcode magic numbers.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
EVIDENCE_DIR = STORAGE_DIR / "evidence"
WEIGHTS_DIR = BASE_DIR / "weights"
DB_PATH = STORAGE_DIR / "visionguard.db"

for d in (UPLOAD_DIR, EVIDENCE_DIR, WEIGHTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


class Settings:
    STORAGE_DIR = STORAGE_DIR
    UPLOAD_DIR = UPLOAD_DIR
    EVIDENCE_DIR = EVIDENCE_DIR
    WEIGHTS_DIR = WEIGHTS_DIR
    DB_PATH = DB_PATH

    CUSTOM_WEIGHTS_PATH: str = os.getenv(
        "VG_CUSTOM_WEIGHTS", str(WEIGHTS_DIR / "helmet_triple_yolov8.pt")
    )
    FALLBACK_WEIGHTS: str = os.getenv("VG_FALLBACK_WEIGHTS", "yolov8n.pt")

    COCO_PERSON_ID: int = 0
    COCO_MOTORCYCLE_ID: int = 3
    COCO_CAR_ID: int = 2
    COCO_BUS_ID: int = 5
    COCO_TRUCK_ID: int = 7

    CUSTOM_CLASS_NAMES = [
        "motorcycle",
        "person",
        "helmet",
        "no_helmet",
        "number_plate",
    ]

    DETECTION_CONFIDENCE_THRESHOLD: float = float(os.getenv("VG_CONF_THRESH", "0.35"))
    TRIPLE_RIDING_MIN_RIDERS: int = 3

    OCR_LANGS = ["en"]
    PLATE_REGEX = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}$"

    RISK_BASE_SCORE = {
        "helmet_non_compliance": 25,
        "triple_riding": 35,
        "seatbelt_violation": 20,
        "wrong_side_driving": 45,
        "red_light_violation": 50,
        "stop_line_violation": 15,
        "illegal_parking": 10,
    }
    RISK_REPEAT_OFFENDER_BONUS = 20
    RISK_LOW_CONFIDENCE_PENALTY = -10

    RISK_BANDS = (
        (0, 20, "Low"),
        (20, 50, "Medium"),
        (50, 75, "High"),
        (75, 1000, "Critical"),
    )

    CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
