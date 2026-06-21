"""
Fine-tune YOLOv8 on your helmet/triple-riding dataset.

1. Annotate your dataset (CVAT, LabelImg, or Roboflow all work) using
   these 5 classes, in this exact order:
       0 motorcycle
       1 person
       2 helmet
       3 no_helmet
       4 number_plate

2. Generate data.yaml:
       python prepare_dataset.py --data_dir /path/to/your_dataset --out data.yaml

3. Train:
       python train_helmet.py --data data.yaml --epochs 80 --model yolov8n.pt

4. Copy the best weights into the running backend:
       cp runs/detect/train/weights/best.pt ../weights/helmet_triple_yolov8.pt

   The backend auto-detects this file on next startup (see
   app/detection/detector.py) — no other code changes needed.
"""
import argparse

from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="Base weights to fine-tune from")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=15,
        project="runs/detect",
        name="train",
    )
    metrics = model.val()
    print("Validation metrics:", metrics.results_dict)
    print(
        "\nBest weights saved to runs/detect/train/weights/best.pt\n"
        "Copy it to ../weights/helmet_triple_yolov8.pt to activate CUSTOM "
        "mode in the running backend."
    )


if __name__ == "__main__":
    main()
