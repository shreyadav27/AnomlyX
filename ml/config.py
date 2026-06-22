"""Central configuration for the AnomlyX ML pipeline.

Updated for 4-class classification with EfficientNetB0 backbone.
Classes: Casting_Defect, Corrosion, Crack, Slag_Inclusion
"""

import os
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ML_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ML_DIR.parent
DATASET_DIR = PROJECT_ROOT / "Defect_Dataset"
SAVED_MODELS_DIR = ML_DIR / "saved_models"
RESULTS_DIR = ML_DIR / "results"

# Ensure output directories exist
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Model paths ──────────────────────────────────────────────────────────────
MODEL_SAVE_PATH = SAVED_MODELS_DIR / "defect_classifier.keras"

# ── Image preprocessing ─────────────────────────────────────────────────────
IMG_SIZE = (224, 224)           # EfficientNetB0 default input size
BATCH_SIZE = 16                 # Balanced for dataset size (~960 images)
INPUT_SHAPE = (*IMG_SIZE, 3)    # (224, 224, 3)

# ── Training hyperparameters ─────────────────────────────────────────────────
EPOCHS_FROZEN = int(os.getenv("ANOMLYX_EPOCHS_FROZEN", "30"))      # Phase 1: train head only
EPOCHS_FINETUNE = int(os.getenv("ANOMLYX_EPOCHS_FINETUNE", "40"))  # Phase 2: fine-tune base top
LEARNING_RATE_FROZEN = 1e-3     # Higher LR for head warm-up
LEARNING_RATE_FINETUNE = 1e-5   # Very low LR for fine-tuning
VALIDATION_SPLIT = 0.20         # 80/20 train-val split
LABEL_SMOOTHING = 0.1           # Prevents overconfident predictions

# ── Dataset class names ──────────────────────────────────────────────────────
# Sorted alphabetically to match tf.keras.utils.image_dataset_from_directory
# default label ordering. Must match Defect_Dataset/ folder names.
CLASS_NAMES = [
    "Casting_Defect",
    "Corrosion",
    "Crack",
    "Slag_Inclusion",
]

NUM_CLASSES = len(CLASS_NAMES)

# ── Data augmentation bounds ─────────────────────────────────────────────────
# Tuned for industrial defect images — moderate augmentation to increase
# effective dataset size without creating unrealistic transformations.
AUGMENTATION_CONFIG = {
    "rotation_factor": 0.15,        # ±15% of 2π (~±54°) — defects can appear at any angle
    "width_shift": 0.15,            # ±15% horizontal shift
    "height_shift": 0.15,           # ±15% vertical shift
    "zoom_range": (-0.15, 0.15),    # ±15% zoom
    "horizontal_flip": True,
    "vertical_flip": True,
    "brightness_range": 0.2,        # ±20% brightness — accounts for lighting variation
    "contrast_range": 0.2,          # ±20% contrast
}
