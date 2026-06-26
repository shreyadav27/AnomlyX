#!/usr/bin/env python3
"""Offline augmentation for minority classes in the AnomlyX dataset.

Generates synthetic training images for underrepresented classes to balance
the dataset before training. This is much more effective than relying solely
on online augmentation during training.

Usage:
    python augment_minority.py

Augmentation transforms:
    - Random rotation (0-360°)
    - Random horizontal/vertical flip
    - Random brightness/contrast adjustment
    - Random zoom/crop
    - Random color jitter
    - Gaussian noise injection

Generated images are saved with 'aug_' prefix in the same class directory.
"""

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from config import AUGMENTATION_TARGET_PER_CLASS, CLASS_NAMES, DATASET_DIR


def random_rotation(img: Image.Image) -> Image.Image:
    """Apply random rotation between 0-360 degrees."""
    angle = random.uniform(0, 360)
    return img.rotate(angle, resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0))


def random_flip(img: Image.Image) -> Image.Image:
    """Random horizontal and/or vertical flip."""
    if random.random() > 0.5:
        img = ImageOps.mirror(img)
    if random.random() > 0.5:
        img = ImageOps.flip(img)
    return img


def random_brightness(img: Image.Image) -> Image.Image:
    """Random brightness adjustment ±30%."""
    factor = random.uniform(0.7, 1.3)
    return ImageEnhance.Brightness(img).enhance(factor)


def random_contrast(img: Image.Image) -> Image.Image:
    """Random contrast adjustment ±30%."""
    factor = random.uniform(0.7, 1.3)
    return ImageEnhance.Contrast(img).enhance(factor)


def random_color(img: Image.Image) -> Image.Image:
    """Random color saturation adjustment ±25%."""
    factor = random.uniform(0.75, 1.25)
    return ImageEnhance.Color(img).enhance(factor)


def random_sharpness(img: Image.Image) -> Image.Image:
    """Random sharpness adjustment."""
    factor = random.uniform(0.5, 2.0)
    return ImageEnhance.Sharpness(img).enhance(factor)


def random_zoom_crop(img: Image.Image) -> Image.Image:
    """Random zoom by cropping a sub-region and resizing back."""
    w, h = img.size
    zoom = random.uniform(0.75, 1.0)
    crop_w = int(w * zoom)
    crop_h = int(h * zoom)
    left = random.randint(0, w - crop_w)
    top = random.randint(0, h - crop_h)
    cropped = img.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((w, h), Image.Resampling.LANCZOS)


def add_gaussian_noise(img: Image.Image, intensity: float = 0.05) -> Image.Image:
    """Add Gaussian noise to the image."""
    arr = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, intensity * 255, arr.shape).astype(np.float32)
    noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy)


def random_blur(img: Image.Image) -> Image.Image:
    """Apply slight Gaussian blur."""
    radius = random.uniform(0.3, 1.2)
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def augment_image(img: Image.Image) -> Image.Image:
    """Apply a random combination of augmentation transforms to an image."""
    transforms = [
        random_rotation,
        random_flip,
        random_brightness,
        random_contrast,
        random_color,
        random_sharpness,
        random_zoom_crop,
        lambda x: add_gaussian_noise(x, random.uniform(0.02, 0.06)),
        random_blur,
    ]

    # Apply 3-6 random transforms
    n_transforms = random.randint(3, 6)
    selected = random.sample(transforms, n_transforms)

    for transform in selected:
        img = transform(img)

    return img


def get_original_images(class_dir: Path) -> list[Path]:
    """Get list of original (non-augmented) image files in a class directory."""
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    return [
        f for f in sorted(class_dir.iterdir())
        if f.is_file()
        and f.suffix.lower() in extensions
        and not f.stem.startswith("aug_")  # Skip previously augmented images
    ]


def augment_class(class_name: str, target_count: int) -> int:
    """Generate augmented images for a single class.

    Args:
        class_name: Name of the class directory.
        target_count: Target total number of images (original + augmented).

    Returns:
        Number of augmented images generated.
    """
    class_dir = DATASET_DIR / class_name
    if not class_dir.exists():
        print(f"  ⚠ Class directory not found: {class_dir}")
        return 0

    original_images = get_original_images(class_dir)
    current_count = len(original_images)

    if current_count >= target_count:
        print(f"  {class_name:20s}: {current_count} images (already at target, skipping)")
        return 0

    images_needed = target_count - current_count
    print(f"  {class_name:20s}: {current_count} original → generating {images_needed} augmented")

    generated = 0
    while generated < images_needed:
        # Cycle through original images
        src_path = original_images[generated % len(original_images)]

        try:
            img = Image.open(src_path).convert("RGB")
            aug_img = augment_image(img)

            # Save with aug_ prefix and unique index
            aug_name = f"aug_{generated:04d}_{src_path.stem}{src_path.suffix}"
            aug_path = class_dir / aug_name
            aug_img.save(aug_path, quality=95)
            generated += 1

        except Exception as e:
            print(f"    ⚠ Failed to augment {src_path.name}: {e}")
            generated += 1  # Skip and continue

    return generated


def clean_augmented_images() -> None:
    """Remove previously generated augmented images."""
    print("\n  Cleaning previous augmented images...")
    total_removed = 0
    for cls in CLASS_NAMES:
        cls_dir = DATASET_DIR / cls
        if not cls_dir.exists():
            continue
        for f in cls_dir.iterdir():
            if f.is_file() and f.stem.startswith("aug_"):
                f.unlink()
                total_removed += 1
    print(f"  Removed {total_removed} previous augmented images")


def main() -> None:
    """Run offline augmentation for all minority classes."""
    print("=" * 60)
    print("  AnomlyX — Offline Minority Class Augmentation")
    print("=" * 60)
    print(f"\n  Target: {AUGMENTATION_TARGET_PER_CLASS} images per class")
    print(f"  Dataset: {DATASET_DIR}\n")

    # Verify dataset exists
    if not DATASET_DIR.exists():
        print(f"❌ Dataset not found at {DATASET_DIR}")
        print("   Run 'python ../dataset/organize_dataset.py' first.")
        return

    # Clean previous augmented images
    clean_augmented_images()

    # Print current class distribution
    print("\n  Current class distribution:")
    for cls in CLASS_NAMES:
        cls_dir = DATASET_DIR / cls
        if cls_dir.exists():
            originals = get_original_images(cls_dir)
            print(f"    {cls:20s}: {len(originals)} original images")

    # Augment minority classes
    print("\n  Generating augmented images...")
    total_generated = 0
    for cls in CLASS_NAMES:
        generated = augment_class(cls, AUGMENTATION_TARGET_PER_CLASS)
        total_generated += generated

    # Print final distribution
    print("\n" + "=" * 60)
    print("  Final class distribution:")
    print("=" * 60)
    total = 0
    for cls in CLASS_NAMES:
        cls_dir = DATASET_DIR / cls
        if cls_dir.exists():
            count = len([f for f in cls_dir.iterdir() if f.is_file()])
            total += count
            originals = len(get_original_images(cls_dir))
            augmented = count - originals
            print(f"    {cls:20s}: {count:>5} total ({originals} original + {augmented} augmented)")

    print(f"    {'TOTAL':20s}: {total:>5} images")
    print(f"\n  ✅ Generated {total_generated} augmented images")
    print("  Ready for training!")


if __name__ == "__main__":
    main()
