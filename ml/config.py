"""Central configuration for the AnomlyX ML pipeline.

Updated for 5-class classification with EfficientNetB0 backbone.
Classes: Casting_Defect, Corrosion, Crack, No_Defect, Slag_Inclusion
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
BATCH_SIZE = 16                 # Balanced for dataset size (~1480 images)
INPUT_SHAPE = (*IMG_SIZE, 3)    # (224, 224, 3)

# ── Training hyperparameters ─────────────────────────────────────────────────
EPOCHS_FROZEN = int(os.getenv("ANOMLYX_EPOCHS_FROZEN", "40"))      # Phase 1: train head only
EPOCHS_FINETUNE = int(os.getenv("ANOMLYX_EPOCHS_FINETUNE", "50"))  # Phase 2: fine-tune base top
LEARNING_RATE_FROZEN = 1e-3     # Higher LR for head warm-up
LEARNING_RATE_FINETUNE = 5e-6   # Very low LR for stable fine-tuning (was 1e-5)
VALIDATION_SPLIT = 0.20         # 80/20 train-val split
LABEL_SMOOTHING = 0.15          # Prevents overconfident predictions (was 0.1)

# ── Dataset class names ──────────────────────────────────────────────────────
# Sorted alphabetically to match tf.keras.utils.image_dataset_from_directory
# default label ordering. Must match Defect_Dataset/ folder names.
CLASS_NAMES = [
    "Casting_Defect",
    "Corrosion",
    "Crack",
    "No_Defect",
    "Slag_Inclusion",
]

NUM_CLASSES = len(CLASS_NAMES)

# ── Data augmentation bounds ─────────────────────────────────────────────────
# Tuned for industrial defect images — stronger augmentation to increase
# effective dataset size without creating unrealistic transformations.
AUGMENTATION_CONFIG = {
    "rotation_factor": 0.20,        # ±20% of 2π (~±72°) — defects can appear at any angle
    "width_shift": 0.20,            # ±20% horizontal shift (was 0.15)
    "height_shift": 0.20,           # ±20% vertical shift (was 0.15)
    "zoom_range": (-0.20, 0.20),    # ±20% zoom (was ±15%)
    "horizontal_flip": True,
    "vertical_flip": True,
    "brightness_range": 0.25,       # ±25% brightness (was 0.2)
    "contrast_range": 0.25,         # ±25% contrast (was 0.2)
}

# ── Mixup / CutMix configuration ────────────────────────────────────────────
MIXUP_ALPHA = 0.2               # Beta distribution alpha for Mixup blending
USE_MIXUP = True                # Enable Mixup training for smoother boundaries

# ── Offline augmentation targets ─────────────────────────────────────────────
# Target image count per class for offline augmentation of minority classes
AUGMENTATION_TARGET_PER_CLASS = 500

# ── Fine-tuning configuration ───────────────────────────────────────────────
FINE_TUNE_FROM = 80             # Unfreeze from layer 80 (was 100) — deeper adaptation
