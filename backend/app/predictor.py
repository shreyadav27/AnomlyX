from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .config import DATASET_DIR, DEFECT_ALIASES, MODEL_PATH, SEVERITIES


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


def predict_image(filename: str, image_bytes: bytes) -> Prediction:
    classes = discover_classes()
    available_defects = [item["defect"] for item in classes]

    if is_model_ready():
        # Hook a TensorFlow, PyTorch, ONNX, or Teachable Machine model here.
        # Keep the response shape stable so the frontend integration does not change.
        return Prediction(
            defect="Unknown",
            severity="unknown",
            confidence=0.0,
            model_ready=True,
            source="model_not_implemented",
            message="Model file was found, but inference code has not been connected yet.",
        )

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
