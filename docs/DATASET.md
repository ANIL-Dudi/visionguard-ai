# Dataset & Annotation Guide

This is the practical companion to `backend/train/README.md` — what to
actually shoot, how to annotate it, and the pitfalls that bite people
on a hackathon timeline.

## Classes (fixed order — must match `app/config.py`)

| id | class | what to box |
|---|---|---|
| 0 | `motorcycle` | the whole bike, including a clear view of where riders sit |
| 1 | `person` | each rider individually, including pillion riders |
| 2 | `helmet` | just the helmet, tight box |
| 3 | `no_helmet` | the bare head region of a rider with no helmet |
| 4 | `number_plate` | the plate itself, tight box |

## Shooting / sourcing images

- **Mix angles**: front-on, rear-on, and ~30–45° oblique. Pure
  side-profile shots make plate OCR much harder and aren't representative
  of most traffic-camera placements.
- **Mix rider counts**: you need real examples of 1, 2, and 3+ riders.
  If every motorcycle image in your dataset has exactly 2 riders, the
  model never learns what "not triple riding" looks like and will be
  noisy at the threshold.
- **Mix helmet states**: include plenty of clean helmet-on examples,
  not just violations. An unbalanced dataset (95% no_helmet) biases the
  model toward predicting no_helmet regardless of input.
- **Vary lighting/time of day** if your real deployment will see both —
  a model trained only on bright daylight will degrade at dusk.
- **Plate legibility varies on purpose**: include some genuinely
  hard-to-read plates (motion blur, dirt, glare) so the model — and the
  OCR confidence score downstream — reflects real-world conditions
  rather than only ever seeing pristine plates.

## Annotation tools

Any of these export to YOLO `.txt` format directly or via a one-click
export option:
- **CVAT** (cvat.ai) — best for teams annotating together
- **LabelImg** — fastest local/offline option for a solo annotator
- **Roboflow** — easiest onboarding, has an "auto-label" assist feature
  that can speed up the first pass (still review every box)

## Folder layout expected by `prepare_dataset.py`

```
your_dataset/
├── images/
│   ├── train/   (80-90% of images)
│   └── val/     (10-20%, held out — don't peek during training)
└── labels/
    ├── train/   (.txt per image, same filename)
    └── val/
```

Each `.txt` line: `<class_id> <x_center> <y_center> <width> <height>`,
all normalized 0–1, one line per box. Most annotation tools write this
automatically — you shouldn't need to hand-write any of it.

## How much data is "enough" for a hackathon

As a rough floor for a usable (not perfect) model:

| class | minimum examples | comfortable |
|---|---|---|
| motorcycle | 150 | 400+ |
| person | 300 | 800+ |
| helmet | 150 | 400+ |
| no_helmet | 150 | 400+ |
| number_plate | 150 | 400+ |

Quality and variety matter more than raw count — 200 well-annotated,
varied images will outperform 1000 near-duplicate frames from the same
fixed camera.

## Sanity-checking your dataset before training

A quick script to catch the most common annotation mistakes (missing
labels, empty label files, wildly out-of-range boxes) is worth writing
before a multi-hour training run, but at minimum:

```bash
# Count images vs labels — these should match
ls your_dataset/images/train | wc -l
ls your_dataset/labels/train | wc -l
```

A mismatch usually means some images have no corresponding label file
(commonly because they truly have no violation and were left
unannotated — YOLO expects an empty `.txt` for "no objects", not a
missing file).
