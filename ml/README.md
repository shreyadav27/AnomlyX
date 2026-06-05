# AnomlyX ML Pipeline

Machine learning pipeline for industrial metal defect classification using transfer learning (MobileNetV2).

## Overview

This module trains a CNN-based image classifier to identify **6 types** of metal defects from inspection images:

| Class | Description | Training Images |
|-------|-------------|---------------:|
| Corrosion | Surface degradation (rust, pitting) | ~74 |
| Crack | Linear fractures (stress, fatigue) | ~55 |
| Misrun | Incomplete casting fill | ~263 |
| Porosity | Gas pockets/cavities | ~264 |
| Shrinkage | Solidification voids | ~263 |
| Slag Inclusion | Trapped non-metallic material | ~34 |

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

## Setup

```bash
cd ml
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

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
