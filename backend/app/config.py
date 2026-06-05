from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent


def resolve_path(value: str, fallback: Path) -> Path:
    if not value:
        return fallback

    path = Path(value)
    if not path.is_absolute():
      path = BASE_DIR / path
    return path.resolve()


DATASET_DIR = resolve_path(
    os.getenv("ANOMLYX_DATASET_DIR", "../Defect_Dataset"),
    PROJECT_ROOT / "Defect_Dataset",
)
MODEL_PATH = resolve_path(os.getenv("ANOMLYX_MODEL_PATH", ""), BASE_DIR / "models" / "model")
MAX_UPLOAD_BYTES = int(os.getenv("ANOMLYX_MAX_UPLOAD_MB", "10")) * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

DEFECT_ALIASES = {
    "porosity": "Porosity",
    "crack": "Crack",
    "slag": "Slag Inclusion",
    "slag_inclusion": "Slag Inclusion",
    "slag-inclusion": "Slag Inclusion",
    "misrun": "Misrun",
    "corrosion": "Corrosion",
    "shrinkage": "Shrinkage",
}

SEVERITIES = ("low", "medium", "high")
