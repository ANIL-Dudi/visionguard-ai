# Setup Guide

## Requirements

- Python 3.10–3.11 (3.12 also works; 3.13 may lag on some ML wheels)
- Node.js 18+
- ~3GB free disk for model weights + dependencies (PyTorch is the bulk of it)
- A GPU is **not** required — everything defaults to CPU (`gpu=False` /
  no `.cuda()` calls anywhere). Training is faster with one, but not needed
  for inference or for fine-tuning on a few hundred images over a
  hackathon timeline.

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On first run, `ultralytics` downloads `yolov8n.pt` (~6MB) automatically —
this needs internet access once. `easyocr` similarly downloads its
recognition model weights on first use (~50–100MB, also one-time).

Check it's healthy:
```bash
curl http://localhost:8000/api/health
```

### Environment variables (optional)

Copy `.env.example` to `.env` to override defaults:
```bash
cp .env.example .env
```
| Variable | Default | Purpose |
|---|---|---|
| `VG_CUSTOM_WEIGHTS` | `weights/helmet_triple_yolov8.pt` | Path checked for fine-tuned weights |
| `VG_FALLBACK_WEIGHTS` | `yolov8n.pt` | Stock model used until custom weights exist |
| `VG_CONF_THRESH` | `0.35` | Minimum detection confidence |

## Frontend

```bash
cd frontend
npm install
npm run dev
```
Opens on http://localhost:5173, proxying `/api` and `/storage` to
`http://localhost:8000` (see `vite.config.js`) — so both servers need
to be running simultaneously in dev.

For a production build:
```bash
npm run build
npm run preview   # or serve dist/ with any static host
```
If you serve the built frontend from a different origin than the
backend, update `CORS_ORIGINS` in `backend/app/config.py` and the API
base URL in `frontend/src/api/client.js`.

## Docker (backend only)

```bash
cd backend
docker build -t visionguard-backend .
docker run -p 8000:8000 -v $(pwd)/storage:/app/storage -v $(pwd)/weights:/app/weights visionguard-backend
```
The volume mounts keep your SQLite DB and trained weights outside the
container so they survive rebuilds.

## Running tests

```bash
cd backend
pip install pytest httpx
pytest -v
```
The smoke tests cover API wiring (health, analytics, violations list,
bad-image rejection, no-violation rejection) without needing trained
weights — they run against whatever detector mode is active.

## Troubleshooting

**"No module named cv2" / opencv import errors on Linux**
Install system libs: `apt-get install -y libgl1 libglib2.0-0` (already
handled in the Dockerfile).

**EasyOCR first run is slow**
That's the one-time model download + CPU warm-up. Subsequent requests
are fast. Consider calling `/api/health` once after starting the
server to pre-warm both the detector and OCR reader before your demo.

**"No violation detected" on every image**
Check `/api/health` → `detector_mode`. In `fallback` mode, detection
quality depends on the stock COCO model actually seeing a clear
`motorcycle` and `person` in frame — try a less cluttered, more
front-on shot, or lower `VG_CONF_THRESH`.

**Plate always "unreadable"**
The classical-CV plate localizer (`detection/plate_ocr.py`) assumes a
roughly front/rear-on shot with the plate in the lower half of the
vehicle bbox. Steep angles or heavily motion-blurred plates will fail
localization — this is exactly the kind of edge case a trained
`number_plate` class (see `docs/DATASET.md`) handles far better.

**Want to reset all demo data**
```bash
rm backend/storage/visionguard.db
rm backend/storage/evidence/*
```
Restart the backend — a fresh DB is created automatically.
