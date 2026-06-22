"""Defect image prediction module.

Supports two modes:
    1. Real ML inference when a trained .keras model can be loaded.
    2. Filename-based fallback when the runtime/model is unavailable.
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .config import (
    CLASS_NAMES,
    CLASS_NAMES_JSON,
    DATASET_DIR,
    DEFECT_ALIASES,
    MODEL_PATH,
    SEVERITIES,
)

_model = None
_model_class_names: list[str] | None = None
_model_load_error: str | None = None


@dataclass(frozen=True)
class Prediction:
    defect: str
    severity: str
    confidence: float
    model_ready: bool
    source: str
    message: str


@dataclass(frozen=True)
class ModelStatus:
    file_found: bool
    loadable: bool
    loaded: bool
    path: str
    class_names: list[str]
    error: str | None = None


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
            if file_path.is_file()
            and file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        )
        classes.append(
            {
                "defect": defect_dir.name,
                "severities": severities,
                "image_count": image_count,
            }
        )
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


def get_model_status(load: bool = False) -> ModelStatus:
    if load:
        _load_model()

    return ModelStatus(
        file_found=is_model_ready(),
        loadable=_model is not None,
        loaded=_model is not None,
        path=str(MODEL_PATH),
        class_names=_model_class_names or CLASS_NAMES,
        error=_model_load_error,
    )


def _load_model():
    """Lazy-load the TensorFlow/Keras model singleton."""
    global _model, _model_class_names, _model_load_error

    if _model is not None:
        return _model, _model_class_names

    if not is_model_ready():
        _model_load_error = f"Model file not found at {MODEL_PATH}."
        return None, None

    try:
        import tensorflow as tf

        print(f"Loading ML model from {MODEL_PATH}...")
        _model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully.")

        if CLASS_NAMES_JSON and CLASS_NAMES_JSON.exists():
            with open(CLASS_NAMES_JSON, encoding="utf-8") as f:
                _model_class_names = json.load(f)
            print(f"Class names: {_model_class_names}")
        else:
            _model_class_names = CLASS_NAMES
            print(f"Using default class names: {_model_class_names}")

        _model_load_error = None
        return _model, _model_class_names

    except Exception as exc:
        _model_load_error = str(exc)
        print(f"Failed to load model: {exc}")
        _model = None
        _model_class_names = None
        return None, None


def _preprocess_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to the EfficientNetB0 input shape."""
    import numpy as np
    import tensorflow as tf
    from PIL import Image

    try:
        from ml.config import IMG_SIZE
    except Exception:
        IMG_SIZE = (224, 224)

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE, Image.Resampling.LANCZOS)
    img_array = np.array(img, dtype=np.float32)

    return np.expand_dims(img_array, axis=0)


def predict_image(filename: str, image_bytes: bytes) -> Prediction:
    classes = discover_classes()
    available_defects = [item["defect"] for item in classes]

    model, class_names = _load_model()
    if model is not None and class_names is not None:
        try:
            import numpy as np

            img = _preprocess_image_bytes(image_bytes)
            predictions = model.predict(img, verbose=0)[0]

            top_idx = int(np.argmax(predictions))
            confidence = float(predictions[top_idx])
            defect = class_names[top_idx]
            display_defect = defect.replace("_", " ")

            _, severity = infer_from_filename(filename, available_defects)
            if severity == "unknown":
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

        except Exception as exc:
            return Prediction(
                defect="Unknown",
                severity="unknown",
                confidence=0.0,
                model_ready=False,
                source="ml_model_error",
                message=f"Model inference failed: {exc}",
            )

    defect, severity = infer_from_filename(filename, available_defects)
    confidence = 0.35 if defect != "Unknown" or severity != "unknown" else 0.0
    status = get_model_status()
    reason = status.error or "No trained model is configured yet."
    return Prediction(
        defect=defect,
        severity=severity,
        confidence=confidence,
        model_ready=False,
        source="filename_stub",
        message=(
            f"{reason} This placeholder only reads defect/severity hints from "
            "the uploaded filename so the API can be tested."
        ),
    )
