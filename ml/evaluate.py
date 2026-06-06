#!/usr/bin/env python3
"""Evaluate the trained AnomlyX defect classifier.

Usage:
    python evaluate.py

Generates:
    ml/results/confusion_matrix.png   — Confusion matrix heatmap
    ml/results/classification_report.txt — Per-class precision/recall/F1
"""

from env_check import ensure_supported_python

ensure_supported_python()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

from config import CLASS_NAMES, MODEL_SAVE_PATH, RESULTS_DIR
from dataset import load_datasets


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
    save_path: str,
) -> None:
    """Generate and save a confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    cm_normalized = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    # Raw counts
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax1,
    )
    ax1.set_title("Confusion Matrix (Counts)", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Predicted")
    ax1.set_ylabel("Actual")

    # Normalized
    sns.heatmap(
        cm_normalized,
        annot=True,
        fmt=".2f",
        cmap="Oranges",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax2,
    )
    ax2.set_title("Confusion Matrix (Normalized)", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Predicted")
    ax2.set_ylabel("Actual")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Confusion matrix saved to {save_path}")


def main() -> None:
    """Run evaluation on the validation set."""
    print("=" * 70)
    print("  AnomlyX Defect Classifier — Evaluation")
    print("=" * 70)

    # ── Load model ───────────────────────────────────────────────────────
    if not MODEL_SAVE_PATH.exists():
        print(f"\n❌ Model not found at {MODEL_SAVE_PATH}")
        print("   Run 'python train.py' first.")
        return

    print(f"\n📦 Loading model from {MODEL_SAVE_PATH}")
    model = tf.keras.models.load_model(MODEL_SAVE_PATH)

    # ── Load validation dataset ──────────────────────────────────────────
    print("\n📦 Loading validation dataset...")
    _, val_ds, class_names = load_datasets()

    # ── Predict on validation set ────────────────────────────────────────
    print("\n🔍 Running predictions on validation set...")
    y_true = []
    y_pred = []

    for images, labels in val_ds:
        predictions = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(predictions, axis=1))

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # ── Classification report ────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  Classification Report")
    print("=" * 70)

    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        digits=4,
    )
    print(report)

    # Save report to file
    report_path = RESULTS_DIR / "classification_report.txt"
    with open(report_path, "w") as f:
        f.write("AnomlyX Defect Classifier — Classification Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(report)
    print(f"  Report saved to {report_path}")

    # ── Confusion matrix ─────────────────────────────────────────────────
    cm_path = str(RESULTS_DIR / "confusion_matrix.png")
    plot_confusion_matrix(y_true, y_pred, class_names, cm_path)

    # ── Overall accuracy ─────────────────────────────────────────────────
    accuracy = np.mean(y_true == y_pred)
    print(f"\n  Overall accuracy: {accuracy:.4f}")
    print(f"  Total validation samples: {len(y_true)}")

    # ── Per-class accuracy ───────────────────────────────────────────────
    print("\n  Per-class accuracy:")
    for i, cls in enumerate(class_names):
        mask = y_true == i
        if mask.sum() > 0:
            cls_acc = np.mean(y_pred[mask] == i)
            print(f"    {cls:20s}: {cls_acc:.4f}  ({mask.sum()} samples)")
        else:
            print(f"    {cls:20s}: N/A  (0 samples)")


if __name__ == "__main__":
    main()
