"""
Dataset prep helper.

Expects your annotated dataset in this layout (standard YOLO format —
this is what tools like Roboflow, LabelImg, and CVAT export to):

    your_dataset/
    ├── images/
    │   ├── train/*.jpg
    │   └── val/*.jpg
    └── labels/
        ├── train/*.txt
        └── val/*.txt

Each label .txt line: <class_id> <x_center> <y_center> <width> <height>
(all normalized 0-1), with class ids matching CUSTOM_CLASS_NAMES order
in backend/app/config.py:
    0 motorcycle
    1 person
    2 helmet
    3 no_helmet
    4 number_plate

Usage:
    python prepare_dataset.py --data_dir /path/to/your_dataset --out data.yaml
"""
import argparse
import sys
from pathlib import Path

import yaml

CLASS_NAMES = ["motorcycle", "person", "helmet", "no_helmet", "number_plate"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True, help="Path to your_dataset/ root")
    parser.add_argument("--out", default="data.yaml")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    train_images = data_dir / "images" / "train"
    val_images = data_dir / "images" / "val"

    if not train_images.exists():
        sys.exit(
            f"Expected {train_images} to exist. See the docstring at the top of "
            "this file for the required folder layout."
        )
    if not val_images.exists():
        print(f"WARNING: {val_images} not found — training will run without validation.")

    config = {
        "path": str(data_dir),
        "train": "images/train",
        "val": "images/val" if val_images.exists() else "images/train",
        "names": {i: n for i, n in enumerate(CLASS_NAMES)},
    }

    with open(args.out, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    n_train = len(list(train_images.glob("*")))
    print(f"Wrote {args.out}")
    print(f"Found {n_train} training images in {train_images}")
    print(f"Classes: {CLASS_NAMES}")


if __name__ == "__main__":
    main()
