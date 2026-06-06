# AnomlyX ML Pipeline

Machine learning pipeline for industrial metal defect classification using transfer learning (MobileNetV2).

## Overview

This module trains a CNN-based image classifier to identify **6 types** of metal defects from inspection images:

| Class | Description | Training Images |
|-------|-------------|---------------:|
| Corrosion | Surface degradation (rust, pitting) | 71 |
| Crack | Linear fractures (stress, fatigue) | 52 |
| Misrun | Incomplete casting fill | 260 |
| Porosity | Gas pockets/cavities | 261 |
| Shrinkage | Solidification voids | 260 |
| Slag Inclusion | Trapped non-metallic material | 31 |

Current dataset size: **935 images** split into **748 training images** and
**187 validation images**.

## Architecture

```text
Input (224×224×3)
  → Data Augmentation (rotation, flip, zoom, brightness, contrast)
  → MobileNetV2 (pretrained ImageNet, partially frozen)
  → GlobalAveragePooling2D
  → Dropout(0.3)
  → Dense(128, ReLU)
  → Dropout(0.3)
  → Dense(6, Softmax)
```

**Two-phase training:**
1. **Phase 1 (Frozen)**: Train only the classification head (~20 epochs)
2. **Phase 2 (Fine-tune)**: Unfreeze top MobileNetV2 layers, train with very low LR (~30 epochs)

## Latest Training Result

The model has been trained and saved locally at
`ml/saved_models/defect_classifier.keras`.

| Metric | Value |
| --- | ---: |
| Phase 1 best validation accuracy | 83.42% |
| Phase 2 best validation accuracy | 83.42% |
| Best overall validation accuracy | 83.42% |
| Total parameters | 2,422,726 |
| Trainable parameters in frozen phase | 164,742 |
| Non-trainable parameters in frozen phase | 2,257,984 |

Training artifacts:

- Model: `saved_models/defect_classifier.keras`
- Class labels: `saved_models/class_names.json`
- Training curves: `results/training_history.png`

The model predicts the six defect types listed above. Severity classification is
not learned by this model yet; backend severity is inferred from filename hints
or confidence thresholds.

## Setup

TensorFlow is required and this project should be run with **Python 3.10, 3.11,
or 3.12**. Python 3.13+ may create a venv successfully, but pip will not find a
compatible TensorFlow wheel.

```bash
cd ml
python3.12 -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

If `python3.12` is not installed on your system, install Python 3.12 first, then
recreate `.venv`.

## Usage

### Train the model

```bash
python train.py
```

This will:
- Load images from `../Defect_Dataset/`
- Train the two-phase model
- Save the best model to `saved_models/defect_classifier.keras`
- Save training curves to `results/training_history.png`

### Evaluate

```bash
python evaluate.py
```

Generates:
- `results/confusion_matrix.png` — Confusion matrix heatmap
- `results/classification_report.txt` — Per-class precision/recall/F1

### Predict on a single image

```bash
python predict.py --image ../Defect_Dataset/Porosity/High/cast_def_0_100.jpeg
python predict.py --image path/to/image.jpg --top 5
```

## File Structure

```text
ml/
├── __init__.py          # Package marker
├── config.py            # Central configuration (paths, hyperparams, classes)
├── dataset.py           # Dataset loading, augmentation, preprocessing
├── model.py             # MobileNetV2 model architecture
├── train.py             # Training pipeline (two-phase)
├── evaluate.py          # Evaluation + confusion matrix
├── predict.py           # Standalone inference CLI
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── saved_models/        # Trained model output (git-ignored)
│   ├── defect_classifier.keras
│   └── class_names.json
└── results/             # Evaluation outputs (git-ignored)
    ├── training_history.png
    ├── confusion_matrix.png
    └── classification_report.txt
```

## Notes

- **Small dataset**: With ~935 total images and class imbalance, expect moderate accuracy. Data augmentation and transfer learning help significantly.
- **GPU recommended**: Training on CPU works but is slow (~30 min). With GPU it takes ~5 min.
- The model integrates with the FastAPI backend in `../backend/` — once trained, the `/predict` endpoint uses real inference.
