# API Reference

Base URL (dev): `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs` (Swagger UI, auto-generated)

## `POST /api/detect`

Run the full pipeline on one image: detection → violation engine →
plate OCR → risk scoring → recommendation → evidence generation →
persisted record.

**Request:** `multipart/form-data`, field `image` (JPG/PNG).

**Response 200:**
```json
{
  "violation_id": "V0001",
  "vehicle_type": "Motorcycle",
  "violation_type": "helmet_non_compliance",
  "violation_label": "Helmet Missing",
  "confidence": 0.96,
  "rider_count": null,
  "boxes": [
    {"label": "motorcycle", "confidence": 0.91, "x1": 200, "y1": 150, "x2": 440, "y2": 400, "kind": "detection"},
    {"label": "no_helmet", "confidence": 0.88, "x1": 220, "y1": 80, "x2": 270, "y2": 130, "kind": "violation"}
  ],
  "plate": {"text": "KA01AB1234", "confidence": 0.92, "valid_format": true},
  "risk": {"score": 25, "level": "Medium", "base_score": 25, "repeat_offender_bonus": 0, "confidence_penalty": 0, "is_repeat_offender": false},
  "recommendation": "Issue standard e-challan.",
  "annotated_image_url": "/api/evidence/V0001/image",
  "timestamp": "2026-06-21T10:15:00"
}
```

**Errors:**
- `400` — image couldn't be decoded
- `422` — no violation detected in the image (includes raw detection labels seen, for debugging)

## `GET /api/evidence/{violation_id}`

Returns the stored JSON record for one violation.

## `GET /api/evidence/{violation_id}/image`

Returns the annotated JPEG (bounding boxes drawn).

## `GET /api/evidence/{violation_id}/card`

Returns the rendered evidence card PNG (photo + structured fields —
what you'd attach to an e-challan).

## `GET /api/analytics/summary`

```json
{
  "total_violations": 120,
  "by_type": {"helmet_non_compliance": 60, "triple_riding": 30},
  "by_risk_level": {"Medium": 70, "High": 50},
  "avg_risk_score": 38.2,
  "repeat_offender_count": 8,
  "plates_flagged": 95,
  "implemented_modules": ["Helmet Non Compliance", "Triple Riding"],
  "architecture_modules": ["Seatbelt Violation", "Wrong Side Driving", "Red Light Violation", "Stop Line Violation", "Illegal Parking"]
}
```

## `GET /api/violations`

Query params: `limit` (default 50, max 500), `violation_type`, `plate_text`.

Returns a list of violation summaries, newest first — powers the
dashboard's recent-violations table and supports plate-based lookups
(used internally for repeat-offender detection).

## `GET /api/health`

Returns detector mode (`custom` or `fallback`) and the live/architecture
module split — useful for a quick "is everything wired up" check before
a demo.
