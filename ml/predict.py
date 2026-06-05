#!/usr/bin/env python3
"""Standalone prediction script for the AnomlyX defect classifier.

Usage:
    python predict.py --image path/to/image.jpg
    python predict.py --image ../Defect_Dataset/Porosity/High/cast_def_0_100.jpeg
    python predict.py --image path/to/image.jpg --top 5

Loads the saved model and returns top-N predictions with confidence scores.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

from config import CLASS_NAMES, IMG_SIZE, MODEL_SAVE_PATH


def load_and_preprocess_image(image_path: str) -> np.ndarray:
    """Load an image file and preprocess it for MobileNetV2.

    Args:
        image_path: Path to the image file.

    Returns:
        Preprocessed image as numpy array with shape (1, 224, 224, 3).
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE, Image.Resampling.LANCZOS)
    img_array = np.array(img, dtype=np.float32)

    # MobileNetV2 preprocessing: scale to [-1, 1]
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    # Add batch dimension
    return np.expand_dims(img_array, axis=0)


def predict(
    model: tf.keras.Model,
    image_path: str,
    class_names: list[str],
    top_n: int = 3,
) -> list[dict]:
    """Run prediction on a single image.

    Returns:
        List of top-N predictions, each with 'class', 'confidence', 'rank'.
    """
    img = load_and_preprocess_image(image_path)
    predictions = model.predict(img, verbose=0)[0]

    # Sort by confidence (descending)
    top_indices = np.argsort(predictions)[::-1][:top_n]

    results = []
    for rank, idx in enumerate(top_indices, 1):
        results.append({
            "rank": rank,
            "class": class_names[idx],
            "confidence": float(predictions[idx]),
        })

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AnomlyX Defect Classifier — Single Image Prediction"
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to the input image (JPG, PNG, or WEBP).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of top predictions to show (default: 3).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Path to saved model (default: {MODEL_SAVE_PATH}).",
    )
    args = parser.parse_args()

    # Validate image path
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return

    # Load model
    model_path = Path(args.model) if args.model else MODEL_SAVE_PATH
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        print("   Run 'python train.py' first.")
        return

    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)

    # Try loading class names from JSON (saved during training)
    class_names_path = model_path.parent / "class_names.json"
    if class_names_path.exists():
        with open(class_names_path) as f:
            class_names = json.load(f)
    else:
        class_names = CLASS_NAMES

    # Run prediction
    print(f"\nAnalyzing: {image_path.name}")
    print("-" * 50)

    results = predict(model, str(image_path), class_names, top_n=args.top)

    for r in results:
        bar_len = int(r["confidence"] * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"  #{r['rank']}  {r['class']:20s}  {bar}  {r['confidence']:.2%}")

    # Highlight top prediction
    top = results[0]
    print(f"\n  🔍 Prediction: {top['class']} ({top['confidence']:.2%} confidence)")


if __name__ == "__main__":
    main()
