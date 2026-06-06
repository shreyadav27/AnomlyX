"""Dataset loading, augmentation, and preprocessing for AnomlyX defect classification.

Uses Defect_Dataset/ which has the structure:
    Defect_Dataset/
    ├── Corrosion/   (Low/ Medium/ High/)
    ├── Crack/       (Low/ Medium/ High/)
    ├── Misrun/      (Low/ Medium/ High/)
    ├── Porosity/    (Low/ Medium/ High/)
    ├── Shrinkage/   (Low/ Medium/ High/)
    └── Slag_Inclusion/ (Low/ Medium/ High/)

Images across all severity sub-folders are merged per defect class for the
defect-type classifier (6 classes).
"""

import shutil
import tempfile
from pathlib import Path

import tensorflow as tf

from config import (
    AUGMENTATION_CONFIG,
    BATCH_SIZE,
    CLASS_NAMES,
    DATASET_DIR,
    IMG_SIZE,
    VALIDATION_SPLIT,
)


def _build_flat_dataset_dir() -> Path:
    """Create a temporary flat directory merging severity sub-folders per defect.

    Defect_Dataset has defect/severity/ sub-dirs but we want defect/ only for
    the 6-class classifier.  We symlink all images into a flat temp structure:
        tmp/
        ├── Corrosion/   (all Low+Medium+High images)
        ├── Crack/
        ...
    """
    flat_dir = Path(tempfile.mkdtemp(prefix="anomlyx_flat_"))
    for cls in CLASS_NAMES:
        class_src = DATASET_DIR / cls
        class_dst = flat_dir / cls
        class_dst.mkdir(parents=True, exist_ok=True)

        if not class_src.exists():
            print(f"  ⚠ Missing class folder: {class_src}")
            continue

        for img_path in class_src.rglob("*"):
            if img_path.is_file() and img_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                dest = class_dst / img_path.name
                # Avoid collisions by prefixing with severity folder name
                if dest.exists():
                    dest = class_dst / f"{img_path.parent.name}_{img_path.name}"
                shutil.copy2(img_path, dest)

    return flat_dir


def build_augmentation_layer() -> tf.keras.Sequential:
    """Data augmentation pipeline applied during training only."""
    aug = AUGMENTATION_CONFIG
    return tf.keras.Sequential(
        [
            tf.keras.layers.RandomRotation(aug["rotation_factor"]),
            tf.keras.layers.RandomTranslation(aug["height_shift"], aug["width_shift"]),
            tf.keras.layers.RandomZoom(aug["zoom_range"]),
            tf.keras.layers.RandomFlip("horizontal_and_vertical"),
            tf.keras.layers.RandomBrightness(aug["brightness_range"]),
            tf.keras.layers.RandomContrast(aug["contrast_range"]),
        ],
        name="data_augmentation",
    )


def load_datasets() -> tuple[tf.data.Dataset, tf.data.Dataset, list[str]]:
    """Load training and validation datasets from Defect_Dataset/.

    Returns:
        (train_ds, val_ds, class_names) — datasets are batched and prefetched.
    """
    print(f"Loading dataset from {DATASET_DIR}")
    print(f"  Image size: {IMG_SIZE}, Batch size: {BATCH_SIZE}")
    print(f"  Validation split: {VALIDATION_SPLIT}")

    # Build flat directory for keras loader
    flat_dir = _build_flat_dataset_dir()
    print(f"  Flat dataset dir: {flat_dir}")

    # Count images per class
    for cls in CLASS_NAMES:
        cls_dir = flat_dir / cls
        count = len(list(cls_dir.iterdir())) if cls_dir.exists() else 0
        print(f"    {cls}: {count} images")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        flat_dir,
        validation_split=VALIDATION_SPLIT,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=True,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        flat_dir,
        validation_split=VALIDATION_SPLIT,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=False,
    )

    discovered_classes = train_ds.class_names
    print(f"  Discovered classes: {discovered_classes}")

    # Verify class ordering matches our config
    assert discovered_classes == CLASS_NAMES, (
        f"Class name mismatch!\n"
        f"  Expected: {CLASS_NAMES}\n"
        f"  Got:      {discovered_classes}\n"
        f"Check Defect_Dataset/ folder names."
    )

    # Apply MobileNetV2 preprocessing (scale pixels to [-1, 1])
    preprocess = tf.keras.applications.mobilenet_v2.preprocess_input

    train_ds = train_ds.map(
        lambda x, y: (preprocess(x), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    val_ds = val_ds.map(
        lambda x, y: (preprocess(x), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    # Performance optimization
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, discovered_classes


if __name__ == "__main__":
    # Quick test: load and inspect the dataset
    train_ds, val_ds, classes = load_datasets()
    print(f"\nClasses: {classes}")
    print(f"Training batches: {len(train_ds)}")
    print(f"Validation batches: {len(val_ds)}")

    for images, labels in train_ds.take(1):
        print(f"Image batch shape: {images.shape}")
        print(f"Label batch shape: {labels.shape}")
        print(f"Pixel range: [{images.numpy().min():.2f}, {images.numpy().max():.2f}]")
