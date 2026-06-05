"""Defect image prediction module.

Supports two modes:
    1. Real ML inference — when a trained .keras model exists at MODEL_PATH.
    2. Filename-based stub — fallback when no model is available.
"""

import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from .config import (
    CLASS_NAMES,
    CLASS_NAMES_JSON,
    DATASET_DIR,
    DEFECT_ALIASES,
    MODEL_PATH,
    SEVERITIES,
)

# ── Lazy-loaded model singleton ──────────────────────────────────────────────
_model = None
_model_class_names: list[str] | None = None


@dataclass(frozen=True)
class Prediction:
    defect: str
    severity: str
    confidence: float
    model_ready: bool
    source: str
    message: str


def normalize_token(value: str) -> str:
    return value.lower().replace("-", "_").replace(" ", "_")


def discover_classes(dataset_dir: Path = DATASET_DIR) -> list[dict[str, object]]:
    if not dataset_dir.exists():
        return []

    classes: list[dict[str, object]] = []
    for defect_dir in sorted(path for path in dataset_dir.iterdir() if path.is_dir()):
        severities = [
            severity_dir.name
            for severity_dir in sorted(path for path in defect_dir.iterdir() if path.is_dir())
        ]
        image_count = sum(
            1
            for file_path in defect_dir.rglob("*")
            if file_path.is_file() and file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        )
        classes.append({
            "defect": defect_dir.name,
            "severities": severities,
            "image_count": image_count,
        })
    return classes


def infer_from_filename(filename: str, available_defects: Iterable[str]) -> tuple[str, str]:
    normalized_name = normalize_token(Path(filename).stem)
    normalized_available = {
        normalize_token(defect): defect.replace("_", " ").title()
        for defect in available_defects
    }

    defect = "Unknown"
    for token, label in {**DEFECT_ALIASES, **normalized_available}.items():
        if normalize_token(token) in normalized_name:
            defect = label
            break

    severity = "unknown"
    for candidate in SEVERITIES:
        if candidate in normalized_name:
            severity = candidate
            break

    return defect, severity


def is_model_ready() -> bool:
    return bool(str(MODEL_PATH)) and MODEL_PATH.exists()


def _load_model():
    """Lazy-load the TensorFlow/Keras model (singleton)."""
    global _model, _model_class_names

    if _model is not None:
        return _model, _model_class_names

    if not is_model_ready():
        return None, None

    try:
        import tensorflow as tf
        print(f"Loading ML model from {MODEL_PATH}...")
        _model = tf.keras.models.load_model(MODEL_PATH)
        print("  Model loaded successfully.")

        # Load class names from JSON saved during training
        if CLASS_NAMES_JSON and CLASS_NAMES_JSON.exists():
            with open(CLASS_NAMES_JSON) as f:
                _model_class_names = json.load(f)
            print(f"  Class names: {_model_class_names}")
        else:
            _model_class_names = CLASS_NAMES
            print(f"  Using default class names: {_model_class_names}")

        return _model, _model_class_names

    except Exception as e:
        print(f"  ⚠ Failed to load model: {e}")
        _model = None
        _model_class_names = None
        return None, None


def _preprocess_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to a preprocessed numpy array for MobileNetV2.

    Returns array with shape (1, 224, 224, 3) scaled to [-1, 1].
    """
    import tensorflow as tf
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224), Image.Resampling.LANCZOS)
    img_array = np.array(img, dtype=np.float32)

    # MobileNetV2 preprocessing: scale pixels to [-1, 1]
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    return np.expand_dims(img_array, axis=0)


def predict_image(filename: str, image_bytes: bytes) -> Prediction:
    classes = discover_classes()
    available_defects = [item["defect"] for item in classes]

    # Try real ML inference
    model, class_names = _load_model()
    if model is not None and class_names is not None:
        try:
            img = _preprocess_image_bytes(image_bytes)
            predictions = model.predict(img, verbose=0)[0]

            top_idx = int(np.argmax(predictions))
            confidence = float(predictions[top_idx])
            defect = class_names[top_idx]

            # Format defect name for display (Slag_Inclusion → Slag Inclusion)
            display_defect = defect.replace("_", " ")

            # Infer severity from filename as a hint (model only predicts defect type)
            _, severity = infer_from_filename(filename, available_defects)
            if severity == "unknown":
                # Default severity based on confidence
                if confidence > 0.85:
                    severity = "high"
                elif confidence > 0.6:
                    severity = "medium"
                else:
                    severity = "low"

            return Prediction(
                defect=display_defect,
                severity=severity,
                confidence=round(confidence, 4),
                model_ready=True,
                source="ml_model",
                message=(
                    f"ML model prediction: {display_defect} "
                    f"({confidence:.1%} confidence). "
                    f"Severity estimated as {severity}."
                ),
            )

        except Exception as e:
            return Prediction(
                defect="Unknown",
                severity="unknown",
                confidence=0.0,
                model_ready=True,
                source="ml_model_error",
                message=f"Model inference failed: {e}",
            )

    # Fallback: filename-based stub
    defect, severity = infer_from_filename(filename, available_defects)
    confidence = 0.35 if defect != "Unknown" or severity != "unknown" else 0.0
    return Prediction(
        defect=defect,
        severity=severity,
        confidence=confidence,
        model_ready=False,
        source="filename_stub",
        message=(
            "No trained model is configured yet. This placeholder only reads defect/severity "
            "hints from the uploaded filename so the API can be tested."
        ),
    )
