# AnomlyX ML Pipeline

Machine learning pipeline for industrial metal defect classification using transfer learning with EfficientNetB0.

## Overview

This module trains a CNN-based image classifier to identify **4 classes** of metal defects from inspection images:

| Class | Description |
|-------|-------------|
| Casting_Defect | Defects from casting process, such as cold shuts or misruns |
| Corrosion | Surface degradation (rust, pitting) |
| Crack | Linear fractures (stress, fatigue) |
| Slag_Inclusion | Trapped non-metallic material |

The current model configuration expects dataset folders under `../Defect_Dataset/` with these exact class names.

## Architecture

```text
Input (224×224×3)
  → EfficientNetB0 backbone (pretrained ImageNet, frozen during Phase 1)
  → GlobalAveragePooling2D
  → BatchNormalization
  → Dropout(0.3)
  → Dense(256, ReLU)
  → BatchNormalization
  → Dropout(0.3)
  → Dense(4, Softmax)
```

**Two-phase training:**
1. **Phase 1 (Frozen)**: Train only the classification head while the EfficientNetB0 base remains frozen.
2. **Phase 2 (Fine-tune)**: Unfreeze the top base layers and continue training with a much lower learning rate.

## Current model details

- Model implementation: `ml/model.py`
- Backbone: `tf.keras.applications.EfficientNetB0`
- Input shape: `224×224×3`
- Number of classes: `4`
- Saved model path: `ml/saved_models/defect_classifier.keras`
- Class labels file: `ml/saved_models/class_names.json`

## Setup

TensorFlow is required. The repository is designed for Python 3.10, 3.11, or 3.12.

```bash
cd ml
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Train the model

```bash
python train.py
```

This will:
- Load images from `../Defect_Dataset/`
- Train the head in Phase 1 with a frozen EfficientNetB0 base
- Optionally unfreeze top base layers and fine-tune in Phase 2
- Save the best model to `saved_models/defect_classifier.keras`

### Evaluate

```bash
python evaluate.py
```

Generates:
- `results/confusion_matrix.png`
- `results/classification_report.txt`

### Predict on a single image

```bash
python predict.py --image ../Defect_Dataset/Corrosion/example.jpg
python predict.py --image path/to/image.jpg --top 5
```

## File Structure

```text
ml/
├── __init__.py
├── config.py            # Central configuration (paths, hyperparams, classes)
├── dataset.py           # Dataset loading, augmentation, preprocessing
├── model.py             # EfficientNetB0-based model architecture
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

- The current model is configured for **4-class defect classification** only.
- The `ml/README.md` now matches the current `ml/model.py` implementation.
- If your dataset or class labels change, update `ml/config.py` accordingly.
