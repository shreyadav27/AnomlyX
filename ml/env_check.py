"""Runtime checks for the AnomlyX ML scripts."""

from __future__ import annotations

import sys


MIN_PYTHON = (3, 10)
MAX_PYTHON_EXCLUSIVE = (3, 13)


def ensure_supported_python() -> None:
    """Exit early with a clear message when TensorFlow cannot be installed."""
    version = sys.version_info
    if MIN_PYTHON <= version[:2] < MAX_PYTHON_EXCLUSIVE:
        return

    supported = "3.10, 3.11, or 3.12"
    current = f"{version.major}.{version.minor}.{version.micro}"
    print(
        "\nUnsupported Python runtime for the AnomlyX ML pipeline.\n"
        f"  Current:   Python {current}\n"
        f"  Required:  Python {supported}\n\n"
        "TensorFlow is required for training and does not provide compatible "
        "wheels for this Python version. Recreate the venv with a supported "
        "interpreter, for example:\n\n"
        "  cd ml\n"
        "  rm -rf .venv\n"
        "  python3.12 -m venv .venv\n"
        "  source .venv/bin/activate\n"
        "  pip install -r requirements.txt\n"
        "  python train.py\n"
    )
    raise SystemExit(1)
