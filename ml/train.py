#!/usr/bin/env python3
"""Train the AnomlyX defect classifier.

Usage:
    python train.py

Two-phase training:
    Phase 1 — Frozen base: train only the classification head.
    Phase 2 — Fine-tune: unfreeze top MobileNetV2 layers and train end-to-end
              with a very low learning rate.

Saves:
    ml/saved_models/defect_classifier.keras   — best model (by val_accuracy)
    ml/results/training_history.png           — accuracy/loss curves
"""

import json

from env_check import ensure_supported_python

ensure_supported_python()

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless training
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from config import (
    CLASS_NAMES,
    EPOCHS_FINETUNE,
    EPOCHS_FROZEN,
    MODEL_SAVE_PATH,
    RESULTS_DIR,
)
from dataset import load_datasets
from model import build_model, get_model_summary, unfreeze_for_finetuning


def get_callbacks(phase: str) -> list[tf.keras.callbacks.Callback]:
    """Training callbacks for a given phase."""
    return [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(MODEL_SAVE_PATH),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=8 if phase == "frozen" else 10,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]


def plot_training_history(
    history_frozen: tf.keras.callbacks.History,
    history_finetune: tf.keras.callbacks.History | None,
    save_path: str,
) -> None:
    """Plot and save training accuracy/loss curves for both phases."""
    acc = history_frozen.history["accuracy"]
    val_acc = history_frozen.history["val_accuracy"]
    loss = history_frozen.history["loss"]
    val_loss = history_frozen.history["val_loss"]

    if history_finetune:
        acc += history_finetune.history["accuracy"]
        val_acc += history_finetune.history["val_accuracy"]
        loss += history_finetune.history["loss"]
        val_loss += history_finetune.history["val_loss"]

    epochs_range = range(1, len(acc) + 1)
    phase1_end = len(history_frozen.history["accuracy"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Accuracy plot
    ax1.plot(epochs_range, acc, label="Train Accuracy", linewidth=2)
    ax1.plot(epochs_range, val_acc, label="Val Accuracy", linewidth=2)
    if history_finetune:
        ax1.axvline(x=phase1_end, color="gray", linestyle="--", alpha=0.7, label="Fine-tune Start")
    ax1.set_title("Model Accuracy", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Accuracy")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Loss plot
    ax2.plot(epochs_range, loss, label="Train Loss", linewidth=2)
    ax2.plot(epochs_range, val_loss, label="Val Loss", linewidth=2)
    if history_finetune:
        ax2.axvline(x=phase1_end, color="gray", linestyle="--", alpha=0.7, label="Fine-tune Start")
    ax2.set_title("Model Loss", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Loss")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Training curves saved to {save_path}")


def main() -> None:
    """Run the full two-phase training pipeline."""
    print("=" * 70)
    print("  AnomlyX Defect Classifier — Training Pipeline")
    print("=" * 70)

    # ── Load dataset ─────────────────────────────────────────────────────
    print("\n📦 Loading dataset...")
    train_ds, val_ds, class_names = load_datasets()

    # Count samples
    train_count = sum(len(labels) for _, labels in train_ds)
    val_count = sum(len(labels) for _, labels in val_ds)
    print(f"\n  Training samples:   {train_count}")
    print(f"  Validation samples: {val_count}")
    print(f"  Classes: {class_names}")

    # ── Build model ──────────────────────────────────────────────────────
    print("\n🏗️  Building model...")
    model = build_model(num_classes=len(class_names))
    print(get_model_summary(model))

    # ── Phase 1: Train with frozen base ──────────────────────────────────
    print("\n" + "=" * 70)
    print("  Phase 1: Training classification head (base frozen)")
    print("=" * 70)

    history_frozen = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_FROZEN,
        callbacks=get_callbacks("frozen"),
        verbose=1,
    )

    best_val_acc_p1 = max(history_frozen.history["val_accuracy"])
    print(f"\n  Phase 1 best val_accuracy: {best_val_acc_p1:.4f}")

    # ── Phase 2: Fine-tune top layers ────────────────────────────────────
    print("\n" + "=" * 70)
    print("  Phase 2: Fine-tuning top MobileNetV2 layers")
    print("=" * 70)

    model = unfreeze_for_finetuning(model, fine_tune_from=100)

    history_finetune = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS_FROZEN + EPOCHS_FINETUNE,
        initial_epoch=len(history_frozen.history["accuracy"]),
        callbacks=get_callbacks("finetune"),
        verbose=1,
    )

    best_val_acc_p2 = max(history_finetune.history["val_accuracy"])
    print(f"\n  Phase 2 best val_accuracy: {best_val_acc_p2:.4f}")

    # ── Save training curves ─────────────────────────────────────────────
    plot_path = str(RESULTS_DIR / "training_history.png")
    plot_training_history(history_frozen, history_finetune, plot_path)

    # ── Save class names alongside model ─────────────────────────────────
    class_names_path = MODEL_SAVE_PATH.parent / "class_names.json"
    with open(class_names_path, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"  Class names saved to {class_names_path}")

    # ── Final summary ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  Training Complete!")
    print("=" * 70)
    print(f"  Model saved to:    {MODEL_SAVE_PATH}")
    print(f"  Best val accuracy: {max(best_val_acc_p1, best_val_acc_p2):.4f}")
    print(f"  Classes:           {class_names}")
    print(f"\n  Next steps:")
    print(f"    1. Run evaluation:  python evaluate.py")
    print(f"    2. Test prediction: python predict.py --image <path>")
    print(f"    3. Start backend:   cd ../backend && uvicorn app.main:app --port 8001")


if __name__ == "__main__":
    main()
