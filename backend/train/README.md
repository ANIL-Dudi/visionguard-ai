# Training your own Helmet + Triple Riding model

The backend ships with a working fallback path (stock YOLOv8n + a
rule-based helmet heuristic) so the whole product runs and demos
correctly with **zero training**. This folder is how you replace that
heuristic with a real model trained on your dataset for full accuracy.

## 1. Annotate

Use CVAT, LabelImg, or Roboflow. Export in YOLO format. Use exactly
these 5 classes, in this order (id matters):

| id | class          |
|----|----------------|
| 0  | motorcycle     |
| 1  | person         |
| 2  | helmet         |
| 3  | no_helmet      |
| 4  | number_plate   |

Folder layout expected:

```
your_dataset/
├── images/
│   ├── train/*.jpg
│   └── val/*.jpg
└── labels/
    ├── train/*.txt
    └── val/*.txt
```

## 2. Generate data.yaml

```bash
python prepare_dataset.py --data_dir /path/to/your_dataset --out data.yaml
```

## 3. Train

```bash
python train_helmet.py --data data.yaml --epochs 80 --model yolov8n.pt
```

For a small dataset (<2000 images), start from `yolov8n.pt` (fastest,
least prone to overfitting). For a larger dataset, `yolov8s.pt` or
`yolov8m.pt` will give better accuracy at the cost of training time.

## 4. Activate

```bash
cp runs/detect/train/weights/best.pt ../weights/helmet_triple_yolov8.pt
```

Restart the backend. `app/detection/detector.py` auto-detects the file
and switches from FALLBACK mode to CUSTOM mode — every other file in
the codebase (violation modules, risk engine, API, frontend) is
unaffected, since they only ever talk to the `VehicleDetector`
abstraction, never to YOLO directly.

## Tips for a hackathon-timeline dataset

- 150-300 well-annotated images per class beats 1000 sloppy ones.
- Vary lighting, camera angle, and rider count — triple riding needs
  examples with 1, 2, and 3+ riders so the model doesn't just learn
  "motorcycle = violation".
- Include some clean "helmet" positives, not just "no_helmet" — an
  unbalanced dataset biases the model toward always predicting
  no_helmet.
