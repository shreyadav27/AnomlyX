"""Dataset loading, augmentation, and preprocessing for AnomlyX defect classification.

Uses Defect_Dataset/ with a flat 5-class structure:
    Defect_Dataset/
    ├── Casting_Defect/   (781 images + augmented)
    ├── Corrosion/        (97 images + augmented)
    ├── Crack/            (52 images + augmented)
    ├── No_Defect/        (519 images + augmented)
    └── Slag_Inclusion/   (31 images + augmented)

Includes stratified splitting, heavy augmentation for minority classes,
Mixup training for smoother decision boundaries, and balanced class weights.
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
    MIXUP_ALPHA,
    USE_MIXUP,
    VALIDATION_SPLIT,
)


def build_augmentation_layer() -> tf.keras.Sequential:
    """Data augmentation pipeline applied during training only.

    Uses stronger augmentation to increase effective dataset size
    without creating unrealistic defect images. Includes GaussianNoise
    for robustness to sensor noise in industrial environments.
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
            tf.keras.layers.GaussianNoise(15.0),  # Noise on [0,255] scale
        ],
        name="data_augmentation",
    )


def mixup_batch(images: tf.Tensor, labels: tf.Tensor, alpha: float = MIXUP_ALPHA) -> tuple:
    """Apply Mixup augmentation to a batch of images and labels.

    Mixup creates virtual training examples by blending pairs of images
    and their labels. This encourages the model to learn smoother decision
    boundaries, reducing overconfidence and improving generalization.

    Args:
        images: Batch of images (B, H, W, C).
        labels: One-hot encoded labels (B, num_classes).
        alpha: Beta distribution parameter controlling blend strength.

    Returns:
        Tuple of (mixed_images, mixed_labels).
    """
    batch_size = tf.shape(images)[0]

    # Sample mixing coefficients from Beta distribution
    lam = tf.numpy_function(
        lambda a: np.random.beta(a, a, size=1).astype(np.float32)[0],
        [alpha],
        tf.float32,
    )
    lam = tf.maximum(lam, 1.0 - lam)  # Ensure lam >= 0.5 so original dominates

    # Random permutation for pairing
    indices = tf.random.shuffle(tf.range(batch_size))
    shuffled_images = tf.gather(images, indices)
    shuffled_labels = tf.gather(labels, indices)

    # Blend images and labels
    mixed_images = lam * images + (1.0 - lam) * shuffled_images
    mixed_labels = lam * labels + (1.0 - lam) * shuffled_labels

    return mixed_images, mixed_labels


def compute_class_weights(data_dir: Path, class_names: list[str]) -> dict[int, float]:
    """Compute balanced class weights to counteract dataset imbalance.

    Uses the sklearn 'balanced' formula:
        weight_i = n_total / (n_classes * n_samples_i)

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
    print(f"  Mixup: {'enabled' if USE_MIXUP else 'disabled'} (alpha={MIXUP_ALPHA})")

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

    def augment_fn(x, y):
        return augmentation(x, training=True), y

    def mixup_fn(x, y):
        return mixup_batch(x, y, alpha=MIXUP_ALPHA)

    train_ds = train_ds.map(augment_fn, num_parallel_calls=tf.data.AUTOTUNE)

    # Apply Mixup after augmentation (on augmented images)
    if USE_MIXUP:
        train_ds = train_ds.map(mixup_fn, num_parallel_calls=tf.data.AUTOTUNE)

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
