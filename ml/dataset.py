"""Dataset loading, augmentation, and preprocessing for AnomlyX defect classification.

Uses Defect_Dataset/ with a flat 4-class structure:
    Defect_Dataset/
    ├── Casting_Defect/   (781 images)
    ├── Corrosion/        (97 images)
    ├── Crack/            (52 images)
    └── Slag_Inclusion/   (31 images)

Includes stratified splitting, heavy augmentation for minority classes,
and balanced class weights to handle the ~25:1 imbalance.
"""

import random
import shutil
import tempfile
from pathlib import Path

import numpy as np
import tensorflow as tf

from config import (
    AUGMENTATION_CONFIG,
    BATCH_SIZE,
    CLASS_NAMES,
    DATASET_DIR,
    IMG_SIZE,
    VALIDATION_SPLIT,
)


def build_augmentation_layer() -> tf.keras.Sequential:
    """Data augmentation pipeline applied during training only.

    Uses moderate augmentation to increase effective dataset size
    without creating unrealistic defect images.
    """
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


def compute_class_weights(data_dir: Path, class_names: list[str]) -> dict[int, float]:
    """Compute balanced class weights to counteract dataset imbalance.

    Uses the sklearn 'balanced' formula:
        weight_i = n_total / (n_classes * n_samples_i)

    For our 4-class dataset:
        Casting_Defect (781 images) → low weight (~0.31)
        Corrosion (97 images)      → moderate weight (~2.49)
        Crack (52 images)          → high weight (~4.64)
        Slag_Inclusion (31 images) → very high weight, clamped to 5.0

    Args:
        data_dir: Path to the dataset directory (with class sub-folders).
        class_names: Ordered list of class names.

    Returns:
        Dict mapping class index → weight for use in model.fit(class_weight=...).
    """
    counts = []
    for cls in class_names:
        cls_dir = data_dir / cls
        count = len([f for f in cls_dir.iterdir() if f.is_file()]) if cls_dir.exists() else 0
        counts.append(count)

    counts_arr = np.array(counts, dtype=np.float64)
    n_total = counts_arr.sum()
    n_classes = len(class_names)

    # Balanced class weights: w_i = total / (n_classes * count_i)
    weights = n_total / (n_classes * counts_arr)

    # Clamp extreme weights to avoid instability (max 5× boost)
    weights = np.clip(weights, 0.3, 5.0)

    class_weight = {i: float(w) for i, w in enumerate(weights)}

    print("\n  Class weights (balanced):")
    for i, cls in enumerate(class_names):
        print(f"    {cls:20s}: {class_weight[i]:.3f}  ({int(counts_arr[i])} images)")

    return class_weight


def load_datasets() -> tuple[tf.data.Dataset, tf.data.Dataset, list[str], dict[int, float]]:
    """Load training and validation datasets from Defect_Dataset/.

    Uses stratified per-class splitting to ensure ALL classes are represented
    in both the training and validation sets.

    Returns:
        (train_ds, val_ds, class_names, class_weights) — datasets are batched
        and prefetched; class_weights is a dict for model.fit(class_weight=...).
    """
    print(f"Loading dataset from {DATASET_DIR}")
    print(f"  Image size: {IMG_SIZE}, Batch size: {BATCH_SIZE}")
    print(f"  Validation split: {VALIDATION_SPLIT}")

    # Verify dataset exists
    if not DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_DIR}\n"
            "Run 'python dataset/organize_dataset.py' first."
        )

    # Count images per class
    print("\n  Dataset contents:")
    for cls in CLASS_NAMES:
        cls_dir = DATASET_DIR / cls
        count = len([f for f in cls_dir.iterdir() if f.is_file()]) if cls_dir.exists() else 0
        print(f"    {cls:20s}: {count} images")

    # Compute class weights using FULL dataset counts
    class_weights = compute_class_weights(DATASET_DIR, CLASS_NAMES)

    # ── Stratified split: manually split each class 80/20 ────────────────
    rng = random.Random(42)

    split_dir = Path(tempfile.mkdtemp(prefix="anomlyx_split_"))
    train_dir = split_dir / "train"
    val_dir = split_dir / "val"

    print("\n  Stratified split (per-class):")
    for cls in CLASS_NAMES:
        cls_src = DATASET_DIR / cls
        train_cls = train_dir / cls
        val_cls = val_dir / cls
        train_cls.mkdir(parents=True, exist_ok=True)
        val_cls.mkdir(parents=True, exist_ok=True)

        images = sorted([f for f in cls_src.iterdir() if f.is_file()])
        rng.shuffle(images)

        n_val = max(2, int(len(images) * VALIDATION_SPLIT))  # At least 2 val images
        val_images = images[:n_val]
        train_images = images[n_val:]

        for img in train_images:
            shutil.copy2(img, train_cls / img.name)
        for img in val_images:
            shutil.copy2(img, val_cls / img.name)

        print(f"    {cls:20s}: {len(train_images)} train, {len(val_images)} val")

    # ── Load from separate train/val directories ─────────────────────────
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=True,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=False,
    )

    discovered_classes = train_ds.class_names
    print(f"\n  Discovered classes: {discovered_classes}")

    # Verify class ordering matches our config
    assert discovered_classes == CLASS_NAMES, (
        f"Class name mismatch!\n"
        f"  Expected: {CLASS_NAMES}\n"
        f"  Got:      {discovered_classes}\n"
        f"Check Defect_Dataset/ folder names."
    )

    # ── Apply preprocessing ──────────────────────────────────────────────
    # EfficientNetB0 expects pixel values in [0, 255] and handles its own
    # preprocessing internally. We apply augmentation on raw pixels [0, 255]
    # for training data only.
    augmentation = build_augmentation_layer()

    train_ds = train_ds.map(
        lambda x, y: (augmentation(x, training=True), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    # No augmentation or preprocessing for validation (EfficientNet handles it)
    # val_ds stays as-is with raw pixel values [0, 255]

    # Performance optimization
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, discovered_classes, class_weights


if __name__ == "__main__":
    # Quick test: load and inspect the dataset
    train_ds, val_ds, classes, weights = load_datasets()
    print(f"\nClasses: {classes}")
    print(f"Class weights: {weights}")
    print(f"Training batches: {len(train_ds)}")
    print(f"Validation batches: {len(val_ds)}")

    for images, labels in train_ds.take(1):
        print(f"Image batch shape: {images.shape}")
        print(f"Label batch shape: {labels.shape}")
        print(f"Pixel range: [{images.numpy().min():.2f}, {images.numpy().max():.2f}]")
