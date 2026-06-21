# VisionGuard AI
### Intelligent Traffic Violation Enforcement Platform

Upload a traffic-camera image → VisionGuard detects the vehicle, flags
helmet/triple-riding violations, reads the number plate, generates
evidence, scores the risk, and logs it to a live analytics dashboard.

```
Traffic Image → AI analyzes image → Detects violation → Reads number plate
→ Generates evidence → Assigns risk score → Stores record → Analytics dashboard
```

## What's actually real here

| Capability               | Status                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| Vehicle detection          | ✅ Live — YOLOv8                                                       |
| Helmet violation detection | ✅ Live — fine-tunable YOLOv8 class, with a working CV heuristic fallback if you haven't trained yet |
| Triple riding detection    | ✅ Live — rider-to-motorcycle association + count threshold            |
| Number plate recognition   | ✅ Live — OpenCV plate localization + EasyOCR                          |
| Evidence generation        | ✅ Live — annotated image + rendered evidence card (PNG)               |
| Risk scoring               | ✅ Live — configurable rule engine                                     |
| Analytics dashboard        | ✅ Live — SQLite-backed, real aggregation                              |
| Officer recommendations    | ✅ Live — rule-based recommendation engine                             |
| Seatbelt / Wrong Side / Red Light / Stop Line / Illegal Parking | 🧩 Architecture-only — wired into the engine registry, each documented with exactly what's needed to bring it online (see `docs/ARCHITECTURE.md`) |

The helmet/triple-riding model ships in **fallback mode** (stock YOLOv8n +
a transparent CV heuristic) so the whole product runs end-to-end with
**zero training**. The moment you fine-tune on your own dataset
(`backend/train/`) and drop the weights into `backend/weights/`, the
backend automatically switches to your model — no code changes.

## Quickstart

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

First run downloads `yolov8n.pt` automatically (needs internet once).
API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 3. Try it

Upload any photo containing a motorcycle with 2+ riders, or a rider
without a helmet. Walk through Upload → Detection → Plate → Evidence →
Risk → Dashboard.

## Train on your own dataset (for full helmet accuracy)

See `backend/train/README.md`. Short version:

```bash
cd backend/train
python prepare_dataset.py --data_dir /path/to/your_dataset --out data.yaml
python train_helmet.py --data data.yaml --epochs 80
cp runs/detect/train/weights/best.pt ../weights/helmet_triple_yolov8.pt
```

Restart the backend — it auto-detects the new weights.

## Project layout

```
visionguard-ai/
├── backend/            FastAPI + YOLOv8 + EasyOCR
│   ├── app/
│   │   ├── detection/  YOLOv8 wrapper, plate OCR
│   │   ├── violations/ Violation Engine (2 live, 5 architecture)
│   │   ├── services/   risk engine, recommendations, evidence, analytics
│   │   └── api/        REST endpoints
│   ├── train/          fine-tuning pipeline for your dataset
│   └── tests/          pytest smoke tests
├── frontend/            React + Vite + Tailwind, 6-screen flow
└── docs/                architecture, API reference, setup, dataset guide
```

## Docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design, violation engine tree, why each unimplemented module needs what it needs
- [`docs/API.md`](docs/API.md) — full REST API reference
- [`docs/SETUP.md`](docs/SETUP.md) — detailed setup, Docker, troubleshooting
- [`docs/DATASET.md`](docs/DATASET.md) — annotation guide for training your own model
