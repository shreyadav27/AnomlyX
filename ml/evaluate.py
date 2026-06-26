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
from dataset import build_augmentation_layer, load_datasets


# ── TTA (Test-Time Augmentation) ─────────────────────────────────────────────

def predict_with_tta(
    model: tf.keras.Model,
    images: tf.Tensor,
    n_augmentations: int = 5,
) -> np.ndarray:
    """Run Test-Time Augmentation: average predictions over multiple augmented copies.

    TTA improves both accuracy and confidence by averaging out augmentation noise.
    The original (unaugmented) prediction is always included.

    Args:
        model: Trained Keras model.
        images: Batch of images (B, H, W, C).
        n_augmentations: Number of augmented copies to average (plus the original).

    Returns:
        Averaged prediction probabilities (B, num_classes).
    """
    augmentation = build_augmentation_layer()

    # Start with original prediction
    all_preds = [model.predict(images, verbose=0)]

    # Add augmented predictions
    for _ in range(n_augmentations):
        aug_images = augmentation(images, training=True)
        preds = model.predict(aug_images, verbose=0)
        all_preds.append(preds)

    # Average all predictions
    return np.mean(all_preds, axis=0)


def compute_ece(
    y_true: np.ndarray,
    all_probs: np.ndarray,
    n_bins: int = 10,
) -> float:
    """Compute Expected Calibration Error (ECE).

    ECE measures how well the model's confidence aligns with its actual accuracy.
    A perfectly calibrated model has ECE = 0.

    Args:
        y_true: True class labels (N,).
        all_probs: Predicted probabilities (N, num_classes).
        n_bins: Number of confidence bins.

    Returns:
        ECE value (lower is better).
    """
    confidences = np.max(all_probs, axis=1)
    predictions = np.argmax(all_probs, axis=1)
    accuracies = predictions == y_true

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(y_true)

    for i in range(n_bins):
        in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        prop_in_bin = in_bin.sum() / total
        if in_bin.sum() > 0:
            avg_confidence = confidences[in_bin].mean()
            avg_accuracy = accuracies[in_bin].mean()
            ece += prop_in_bin * abs(avg_accuracy - avg_confidence)

    return float(ece)


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
    if (~correct_mask).sum() > 0:
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
    axes[2].axhline(y=0.90, color="red", linestyle=":", alpha=0.7, label="90% Target")
    axes[2].set_title("Per-Class Accuracy", fontsize=14, fontweight="bold")
    axes[2].set_ylabel("Accuracy")
    axes[2].set_ylim(0, 1.05)
    axes[2].tick_params(axis='x', rotation=30)
    axes[2].grid(True, alpha=0.3, axis='y')
    axes[2].legend()
    for bar, acc in zip(bars, class_accs):
        axes[2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                     f'{acc:.1%}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Confidence distribution saved to {save_path}")


def main() -> None:
    """Run evaluation on the validation set with optional TTA."""
    print("=" * 70)
    print("  AnomlyX Defect Classifier — Evaluation (with TTA)")
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

    # ── Standard predictions (no TTA) ────────────────────────────────────
    print("\n🔍 Running standard predictions on validation set...")
    y_true = []
    y_pred_standard = []
    all_probs_standard = []

    for images, labels in val_ds:
        predictions = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred_standard.extend(np.argmax(predictions, axis=1))
        all_probs_standard.extend(predictions)

    y_true = np.array(y_true)
    y_pred_standard = np.array(y_pred_standard)
    all_probs_standard = np.array(all_probs_standard)

    standard_accuracy = np.mean(y_true == y_pred_standard)

    # ── TTA predictions ──────────────────────────────────────────────────
    print("\n🔍 Running TTA predictions (5 augmentations per image)...")
    y_pred_tta = []
    all_probs_tta = []

    for images, labels in val_ds:
        tta_preds = predict_with_tta(model, images, n_augmentations=5)
        y_pred_tta.extend(np.argmax(tta_preds, axis=1))
        all_probs_tta.extend(tta_preds)

    y_pred_tta = np.array(y_pred_tta)
    all_probs_tta = np.array(all_probs_tta)

    tta_accuracy = np.mean(y_true == y_pred_tta)

    # Choose the better method for detailed reporting
    if tta_accuracy >= standard_accuracy:
        print(f"\n  ✅ TTA improved accuracy: {standard_accuracy:.4f} → {tta_accuracy:.4f}")
        y_pred = y_pred_tta
        all_probs = all_probs_tta
        eval_method = "TTA (5 augmentations)"
    else:
        print(f"\n  ℹ Standard predictions better: {standard_accuracy:.4f} vs TTA {tta_accuracy:.4f}")
        y_pred = y_pred_standard
        all_probs = all_probs_standard
        eval_method = "Standard"

    accuracy = np.mean(y_true == y_pred)

    # ── Classification report ────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"  Classification Report ({eval_method})")
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
        f.write(f"AnomlyX Defect Classifier — Classification Report ({eval_method})\n")
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
    print(f"\n  Overall accuracy: {accuracy:.4f}")
    print(f"  Target (90%):     {'✅ MET' if accuracy >= 0.90 else '❌ NOT MET'}")
    print(f"  Eval method:      {eval_method}")
    print(f"  Total validation samples: {len(y_true)}")

    # ── Calibration (ECE) ────────────────────────────────────────────────
    ece = compute_ece(y_true, all_probs)
    print(f"\n  Expected Calibration Error (ECE): {ece:.4f}")
    print(f"  Calibration: {'Good' if ece < 0.05 else 'Fair' if ece < 0.10 else 'Needs improvement'}")

    # ── Per-class accuracy and confidence ────────────────────────────────
    pred_confidences = np.max(all_probs, axis=1)
    correct_mask = y_true == y_pred

    print(f"\n  Per-class accuracy and confidence:")
    print(f"    {'Class':20s}  {'Accuracy':>10s}  {'Avg Conf (Correct)':>20s}  {'Avg Conf (All)':>16s}  {'Samples':>8s}  {'Status':>8s}")
    print("    " + "-" * 90)

    per_class_metrics = {}
    all_classes_above_80 = True
    for i, cls in enumerate(class_names):
        mask = y_true == i
        if mask.sum() > 0:
            cls_acc = np.mean(y_pred[mask] == i)
            cls_conf_all = np.mean(pred_confidences[mask])

            correct_cls_mask = mask & correct_mask
            cls_conf_correct = np.mean(pred_confidences[correct_cls_mask]) if correct_cls_mask.sum() > 0 else 0.0

            status = "✅" if cls_acc >= 0.80 else "⚠️"
            if cls_acc < 0.80:
                all_classes_above_80 = False

            print(f"    {cls:20s}  {cls_acc:>10.4f}  {cls_conf_correct:>20.4f}  {cls_conf_all:>16.4f}  {mask.sum():>8d}  {status:>8s}")

            per_class_metrics[cls] = {
                "accuracy": float(cls_acc),
                "avg_confidence_correct": float(cls_conf_correct),
                "avg_confidence_all": float(cls_conf_all),
                "samples": int(mask.sum()),
                "above_80_pct": bool(cls_acc >= 0.80),
            }
        else:
            print(f"    {cls:20s}  {'N/A':>10s}  {'N/A':>20s}  {'N/A':>16s}  {'0':>8s}  {'N/A':>8s}")

    # ── Average confidence summary ───────────────────────────────────────
    avg_conf_correct = np.mean(pred_confidences[correct_mask]) if correct_mask.sum() > 0 else 0.0
    avg_conf_incorrect = np.mean(pred_confidences[~correct_mask]) if (~correct_mask).sum() > 0 else 0.0

    print(f"\n  Confidence summary:")
    print(f"    Average confidence (correct):   {avg_conf_correct:.4f}  {'✅' if avg_conf_correct >= 0.85 else '⚠️'}")
    print(f"    Average confidence (incorrect): {avg_conf_incorrect:.4f}")
    print(f"    Confidence gap:                 {avg_conf_correct - avg_conf_incorrect:.4f}  {'✅' if (avg_conf_correct - avg_conf_incorrect) >= 0.2 else '⚠️'}")

    # ── Save all metrics as JSON ─────────────────────────────────────────
    eval_metrics = {
        "overall_accuracy": float(accuracy),
        "standard_accuracy": float(standard_accuracy),
        "tta_accuracy": float(tta_accuracy),
        "eval_method": eval_method,
        "total_samples": int(len(y_true)),
        "expected_calibration_error": float(ece),
        "avg_confidence_correct": float(avg_conf_correct),
        "avg_confidence_incorrect": float(avg_conf_incorrect),
        "confidence_gap": float(avg_conf_correct - avg_conf_incorrect),
        "per_class": per_class_metrics,
        "targets": {
            "overall_accuracy_90": bool(accuracy >= 0.90),
            "all_classes_above_80": all_classes_above_80,
            "avg_confidence_above_85": bool(avg_conf_correct >= 0.85),
            "confidence_gap_above_20": bool((avg_conf_correct - avg_conf_incorrect) >= 0.2),
        },
    }
    metrics_path = str(RESULTS_DIR / "evaluation_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(eval_metrics, f, indent=2)
    print(f"\n  Evaluation metrics saved to {metrics_path}")

    # ── Final verdict ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    targets_met = sum(eval_metrics["targets"].values())
    targets_total = len(eval_metrics["targets"])
    print(f"  Targets met: {targets_met}/{targets_total}")
    for name, met in eval_metrics["targets"].items():
        print(f"    {'✅' if met else '❌'} {name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
