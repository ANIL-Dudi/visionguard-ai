# Architecture

## High-level flow

```
Traffic Image
      ↓
[FastAPI] /api/detect
      ↓
VehicleDetector (YOLOv8) ── custom fine-tuned weights, or fallback to
      ↓                      stock YOLOv8n + CV heuristics
ViolationEngine.run()
      ↓
┌─────────────────────────────────────────┐
│  Per-violation: Risk Engine              │
│       → Recommendation Engine            │
│       → Evidence Service (image + card)  │
└─────────────────────────────────────────┘
      ↓
SQLite (ViolationRecord)
      ↓
Analytics Service ── /api/analytics/summary, /api/violations
```

## The Violation Engine

This is the part of the spec that asked to "show support for" five
additional violation types through system design. We didn't want that
to mean five empty folders — so every module, implemented or not,
shares one interface (`ViolationModule.evaluate()`) and is registered
in the same place. Unimplemented modules raise a typed
`NotImplementedYet(module, requirement_note)` that the engine catches
and surfaces through `/api/health` and `/api/analytics/summary` as
"architecture" rather than silently lying about what's running.

```
ViolationEngine (app/violations/engine.py)
├── HelmetModule          [LIVE]   app/violations/helmet.py
├── TripleRidingModule    [LIVE]   app/violations/triple_riding.py
├── SeatbeltModule        [arch]   app/violations/seatbelt.py
├── WrongSideModule       [arch]   app/violations/wrong_side.py
├── RedLightModule        [arch]   app/violations/red_light.py
├── StopLineModule        [arch]   app/violations/stop_line.py
└── IllegalParkingModule  [arch]   app/violations/illegal_parking.py
```

### Why the other five aren't live yet — and what each needs

| Module | Blocker | What "live" requires |
|---|---|---|
| **Seatbelt** | Needs a trained class | A `seatbelt`/`no_seatbelt` class on windshield-region crops + front-facing camera angle metadata (seatbelts aren't visible from the side/rear). |
| **Wrong Side Driving** | Needs motion, not a single frame | Per-camera lane-direction calibration + multi-frame vehicle tracking (optical flow / Kalman) to derive a motion vector. Structurally impossible from one still image. |
| **Red Light** | Needs external signal state | A live signal-state feed, or an in-frame traffic-light-color classifier, plus a calibrated stop-line ROI. |
| **Stop Line** | Needs calibration + multi-frame | One-time operator-drawn stop-line ROI per camera, then a geometry check across consecutive frames confirming the vehicle was stationary across the line. No new training needed. |
| **Illegal Parking** | Needs calibration + dwell time | A no-parking-zone ROI per camera + a dwell-time threshold (e.g., stationary >2 min). Reuses existing `car`/`truck`/`motorcycle` detections — no new class. |

Helmet and Triple Riding were chosen to be live first because they're
solvable from a **single still image with no camera calibration** —
exactly the constraint of an image-upload demo. The other five need
either new training data (Seatbelt) or a multi-frame/video feed and
per-camera calibration (the other four) — which is a deployment-stage
investment, not a modeling problem, and is the natural next phase after
this MVP.

## Detector: custom vs fallback mode

```
app/detection/detector.py

  weights/helmet_triple_yolov8.pt exists?
        │
   yes ─┤── CUSTOM MODE: your fine-tuned YOLOv8, 5 classes
        │   (motorcycle, person, helmet, no_helmet, number_plate)
        │
   no ──┴── FALLBACK MODE: stock yolov8n.pt (COCO classes)
            + helmet presence inferred via a CV heuristic
              (head-region texture variance + HSV skin-tone ratio)
```

Every other file in the codebase — violation modules, risk engine, API
layer, frontend — only ever talks to `VehicleDetector`, never to YOLO
directly. Swapping in your trained weights is a file copy, not a
refactor.

## Number Plate Recognition pipeline

```
vehicle bbox crop
      ↓
grayscale → bilateral filter → Canny edges → contour search
      ↓
rectangular, plate-shaped candidate (aspect ratio 1.8–5.5)
      ↓
EasyOCR on the localized crop (falls back to full vehicle crop)
      ↓
clean text → validate against Indian plate regex
```

This works in fallback mode too — no trained `number_plate` class is
required, since the geometry heuristic does the localization.

## Risk scoring

```
score = base_score[violation_type]
      + 20 × prior_violations_on_same_plate
      − 10  (if detection_confidence < 0.6)

bands: 0–20 Low · 20–50 Medium · 50–75 High · 75–100 Critical
```

All weights live in `app/config.py` — tune them without touching logic.

## Data model

One `ViolationRecord` row per detected violation: vehicle type,
violation type/label, confidence, plate text + confidence, rider count,
risk score/level, recommendation, repeat-offender flag, and the raw
bounding boxes (for re-rendering the overlay later without re-running
detection).
