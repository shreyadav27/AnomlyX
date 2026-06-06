"""Central configuration for the AnomlyX ML pipeline."""

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
IMG_SIZE = (224, 224)           # MobileNetV2 default input size
BATCH_SIZE = 16                 # Small batches for small dataset
INPUT_SHAPE = (*IMG_SIZE, 3)   # (224, 224, 3)

# ── Training hyperparameters ─────────────────────────────────────────────────
EPOCHS_FROZEN = 20              # Phase 1: train head only (base frozen)
EPOCHS_FINETUNE = 30            # Phase 2: fine-tune top layers of base
LEARNING_RATE_FROZEN = 1e-3     # Higher LR for head warm-up
LEARNING_RATE_FINETUNE = 1e-5   # Very low LR for fine-tuning
VALIDATION_SPLIT = 0.20         # 80/20 train-val split

# ── Dataset class names ──────────────────────────────────────────────────────
# Sorted alphabetically to match tf.keras.utils.image_dataset_from_directory
# default label ordering. Verified against Defect_Dataset/ folder names.
CLASS_NAMES = [
    "Corrosion",
    "Crack",
    "Misrun",
    "Porosity",
    "Shrinkage",
    "Slag_Inclusion",
]

NUM_CLASSES = len(CLASS_NAMES)

# ── Data augmentation bounds ─────────────────────────────────────────────────
AUGMENTATION_CONFIG = {
    "rotation_factor": 0.15,       # ±15% of 2π (~±54°)
    "width_shift": 0.2,            # ±20% horizontal shift
    "height_shift": 0.2,           # ±20% vertical shift
    "zoom_range": 0.2,             # ±20% zoom
    "horizontal_flip": True,
    "vertical_flip": True,
    "brightness_range": 0.2,       # ±20% brightness
    "contrast_range": 0.2,         # ±20% contrast
}
