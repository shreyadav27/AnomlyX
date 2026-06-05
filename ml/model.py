"""MobileNetV2 transfer learning model for defect classification.

Architecture:
    Input (224×224×3)
    → Data Augmentation (training only)
    → MobileNetV2 base (pretrained ImageNet, frozen initially)
    → GlobalAveragePooling2D
    → Dropout(0.3)
    → Dense(128, ReLU)
    → Dropout(0.3)
    → Dense(6, Softmax)
"""

import tensorflow as tf

from config import IMG_SIZE, INPUT_SHAPE, LEARNING_RATE_FINETUNE, LEARNING_RATE_FROZEN, NUM_CLASSES
from dataset import build_augmentation_layer


def build_model(num_classes: int = NUM_CLASSES) -> tf.keras.Model:
    """Build the defect classifier with MobileNetV2 backbone.

    Returns a compiled model with the base frozen (Phase 1 training).
    """
    # Input layer
    inputs = tf.keras.Input(shape=INPUT_SHAPE, name="input_image")

    # Data augmentation (only active during training)
    x = build_augmentation_layer()(inputs)

    # MobileNetV2 backbone — frozen for Phase 1
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=INPUT_SHAPE,
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    x = base_model(x, training=False)

    # Classification head
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout_1")(x)
    x = tf.keras.layers.Dense(128, activation="relu", name="dense_hidden")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout_2")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="anomlyx_defect_classifier")

    # Compile for Phase 1 (frozen base)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE_FROZEN),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    # Store base_model reference for fine-tuning phase
    model._base_model = base_model

    return model


def unfreeze_for_finetuning(model: tf.keras.Model, fine_tune_from: int = 100) -> tf.keras.Model:
    """Unfreeze the top layers of the MobileNetV2 base for Phase 2 fine-tuning.

    Args:
        model: The model returned by build_model().
        fine_tune_from: Layer index in the base model from which to unfreeze.
            MobileNetV2 has 154 layers. Default 100 unfreezes ~35% of layers.

    Returns:
        The same model, recompiled with a lower learning rate.
    """
    base_model = model._base_model
    base_model.trainable = True

    # Freeze everything below fine_tune_from
    for layer in base_model.layers[:fine_tune_from]:
        layer.trainable = False

    trainable_count = sum(1 for layer in base_model.layers if layer.trainable)
    frozen_count = sum(1 for layer in base_model.layers if not layer.trainable)
    print(f"\nFine-tuning: {trainable_count} trainable, {frozen_count} frozen layers in base")

    # Recompile with much lower LR to avoid destroying pretrained weights
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE_FINETUNE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def get_model_summary(model: tf.keras.Model) -> str:
    """Return model summary as a string."""
    lines: list[str] = []
    model.summary(print_fn=lambda line: lines.append(line))
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick test: build and inspect the model
    m = build_model()
    print(get_model_summary(m))
    print(f"\nTotal params: {m.count_params():,}")

    # Test fine-tuning phase
    m = unfreeze_for_finetuning(m)
    print(f"After unfreeze — Total params: {m.count_params():,}")
