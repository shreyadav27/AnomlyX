#!/usr/bin/env python3
"""Evaluate the trained AnomlyX defect classifier.

Usage:
    python evaluate.py

Generates:
    ml/results/confusion_matrix.png        — Confusion matrix heatmap
    ml/results/classification_report.txt   — Per-class precision/recall/F1
    ml/results/evaluation_metrics.json     — All metrics in JSON format
    ml/results/confidence_distribution.png — Confidence distribution per class
"""

from env_check import ensure_supported_python

ensure_supported_python()

import json

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
    all_labels = list(range(len(class_names)))
    cm = confusion_matrix(y_true, y_pred, labels=all_labels)
    # Avoid division by zero for classes with no true samples
    row_sums = cm.sum(axis=1)[:, np.newaxis]
    row_sums[row_sums == 0] = 1
    cm_normalized = cm.astype("float") / row_sums

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

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


def plot_confidence_distribution(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    all_probs: np.ndarray,
    class_names: list[str],
    save_path: str,
) -> None:
    """Plot confidence distribution for correct vs incorrect predictions."""
    pred_confidences = np.max(all_probs, axis=1)
    correct_mask = y_true == y_pred

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Overall confidence distribution
    axes[0].hist(pred_confidences[correct_mask], bins=20, alpha=0.7, label="Correct", color="green", density=True)
    axes[0].hist(pred_confidences[~correct_mask], bins=20, alpha=0.7, label="Incorrect", color="red", density=True)
    axes[0].set_title("Confidence Distribution", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Confidence")
    axes[0].set_ylabel("Density")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Per-class confidence for correct predictions
    class_confs = []
    class_labels = []
    for i, cls in enumerate(class_names):
        mask = (y_true == i) & correct_mask
        if mask.sum() > 0:
            class_confs.extend(pred_confidences[mask].tolist())
            class_labels.extend([cls] * int(mask.sum()))

    if class_confs:
        # Box plot of per-class confidence
        unique_labels = list(dict.fromkeys(class_labels))
        data = [[c for c, l in zip(class_confs, class_labels) if l == ul] for ul in unique_labels]
        bp = axes[1].boxplot(data, labels=unique_labels, patch_artist=True)
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
        axes[1].set_title("Per-Class Confidence (Correct)", fontsize=14, fontweight="bold")
        axes[1].set_ylabel("Confidence")
        axes[1].tick_params(axis='x', rotation=30)
        axes[1].grid(True, alpha=0.3)

    # Per-class accuracy bar chart
    class_accs = []
    for i, cls in enumerate(class_names):
        mask = y_true == i
        if mask.sum() > 0:
            class_accs.append(np.mean(y_pred[mask] == i))
        else:
            class_accs.append(0.0)

    bars = axes[2].bar(class_names, class_accs, color=plt.cm.viridis(np.array(class_accs)))
    axes[2].set_title("Per-Class Accuracy", fontsize=14, fontweight="bold")
    axes[2].set_ylabel("Accuracy")
    axes[2].set_ylim(0, 1.05)
    axes[2].tick_params(axis='x', rotation=30)
    axes[2].grid(True, alpha=0.3, axis='y')
    for bar, acc in zip(bars, class_accs):
        axes[2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                     f'{acc:.1%}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Confidence distribution saved to {save_path}")


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
    _, val_ds, class_names, _ = load_datasets()

    # ── Predict on validation set ────────────────────────────────────────
    print("\n🔍 Running predictions on validation set...")
    y_true = []
    y_pred = []
    all_probs = []

    for images, labels in val_ds:
        predictions = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(predictions, axis=1))
        all_probs.extend(predictions)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    all_probs = np.array(all_probs)

    # ── Classification report ────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  Classification Report")
    print("=" * 70)

    all_labels = list(range(len(class_names)))
    report = classification_report(
        y_true,
        y_pred,
        labels=all_labels,
        target_names=class_names,
        digits=4,
        zero_division=0,
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

    # ── Confidence distribution ──────────────────────────────────────────
    conf_path = str(RESULTS_DIR / "confidence_distribution.png")
    plot_confidence_distribution(y_true, y_pred, all_probs, class_names, conf_path)

    # ── Overall accuracy ─────────────────────────────────────────────────
    accuracy = np.mean(y_true == y_pred)
    print(f"\n  Overall accuracy: {accuracy:.4f}")
    print(f"  Total validation samples: {len(y_true)}")

    # ── Per-class accuracy and confidence ────────────────────────────────
    pred_confidences = np.max(all_probs, axis=1)
    correct_mask = y_true == y_pred

    print("\n  Per-class accuracy and confidence:")
    print(f"    {'Class':20s}  {'Accuracy':>10s}  {'Avg Conf (Correct)':>20s}  {'Avg Conf (All)':>16s}  {'Samples':>8s}")
    print("    " + "-" * 80)

    per_class_metrics = {}
    for i, cls in enumerate(class_names):
        mask = y_true == i
        if mask.sum() > 0:
            cls_acc = np.mean(y_pred[mask] == i)
            cls_conf_all = np.mean(pred_confidences[mask])

            correct_cls_mask = mask & correct_mask
            cls_conf_correct = np.mean(pred_confidences[correct_cls_mask]) if correct_cls_mask.sum() > 0 else 0.0

            print(f"    {cls:20s}  {cls_acc:>10.4f}  {cls_conf_correct:>20.4f}  {cls_conf_all:>16.4f}  {mask.sum():>8d}")

            per_class_metrics[cls] = {
                "accuracy": float(cls_acc),
                "avg_confidence_correct": float(cls_conf_correct),
                "avg_confidence_all": float(cls_conf_all),
                "samples": int(mask.sum()),
            }
        else:
            print(f"    {cls:20s}  {'N/A':>10s}  {'N/A':>20s}  {'N/A':>16s}  {'0':>8s}")

    # ── Average confidence summary ───────────────────────────────────────
    avg_conf_correct = np.mean(pred_confidences[correct_mask]) if correct_mask.sum() > 0 else 0.0
    avg_conf_incorrect = np.mean(pred_confidences[~correct_mask]) if (~correct_mask).sum() > 0 else 0.0

    print(f"\n  Confidence summary:")
    print(f"    Average confidence (correct):   {avg_conf_correct:.4f}")
    print(f"    Average confidence (incorrect): {avg_conf_incorrect:.4f}")
    print(f"    Confidence gap:                 {avg_conf_correct - avg_conf_incorrect:.4f}")

    # ── Save all metrics as JSON ─────────────────────────────────────────
    eval_metrics = {
        "overall_accuracy": float(accuracy),
        "total_samples": int(len(y_true)),
        "avg_confidence_correct": float(avg_conf_correct),
        "avg_confidence_incorrect": float(avg_conf_incorrect),
        "per_class": per_class_metrics,
    }
    metrics_path = str(RESULTS_DIR / "evaluation_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(eval_metrics, f, indent=2)
    print(f"\n  Evaluation metrics saved to {metrics_path}")


if __name__ == "__main__":
    main()
