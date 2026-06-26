"""EfficientNetB0 transfer learning model for defect classification.

Architecture:
    Input (224×224×3)  — preprocessed by tf.keras.applications.efficientnet
    → EfficientNetB0 base (pretrained ImageNet, frozen initially)
    → GlobalAveragePooling2D
    → BatchNormalization
    → Dropout(0.4)
    → Dense(512, ReLU, L2=1e-4)
    → BatchNormalization
    → Dropout(0.4)
    → Dense(256, ReLU, L2=1e-4)
    → BatchNormalization
    → Dropout(0.3)
    → Dense(5, Softmax)

Upgraded architecture with deeper classification head, L2 regularization,
and higher dropout for better generalization on small industrial defect datasets.
"""

import tensorflow as tf

from config import (
    FINE_TUNE_FROM,
    IMG_SIZE,
    INPUT_SHAPE,
    LABEL_SMOOTHING,
    LEARNING_RATE_FINETUNE,
    LEARNING_RATE_FROZEN,
    NUM_CLASSES,
)


def build_model(num_classes: int = NUM_CLASSES) -> tf.keras.Model:
    """Build the defect classifier with EfficientNetB0 backbone.

    Returns a compiled model with the base frozen (Phase 1 training).
    Features a deeper classification head with L2 regularization for
    better feature extraction and reduced overfitting.
    """
    # Input layer
    inputs = tf.keras.Input(shape=INPUT_SHAPE, name="input_image")

    # EfficientNetB0 backbone — frozen for Phase 1
    # EfficientNetB0 has its own preprocessing built-in (scales to [0,1] internally)
    base_model = tf.keras.applications.EfficientNetB0(
        input_shape=INPUT_SHAPE,
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    x = base_model(inputs, training=False)

    # Classification head — deeper with L2 regularization
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = tf.keras.layers.BatchNormalization(name="bn_1")(x)
    x = tf.keras.layers.Dropout(0.4, name="dropout_1")(x)

    # First hidden layer — wider for richer feature combinations
    x = tf.keras.layers.Dense(
        512,
        activation="relu",
        kernel_regularizer=tf.keras.regularizers.l2(1e-4),
        name="dense_hidden_1",
    )(x)
    x = tf.keras.layers.BatchNormalization(name="bn_2")(x)
    x = tf.keras.layers.Dropout(0.4, name="dropout_2")(x)

    # Second hidden layer — narrows features for classification
    x = tf.keras.layers.Dense(
        256,
        activation="relu",
        kernel_regularizer=tf.keras.regularizers.l2(1e-4),
        name="dense_hidden_2",
    )(x)
    x = tf.keras.layers.BatchNormalization(name="bn_3")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout_3")(x)

    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="anomlyx_defect_classifier")

    # Compile for Phase 1 (frozen base) with label smoothing
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE_FROZEN),
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
        metrics=["accuracy"],
    )

    # Store base_model reference for fine-tuning phase
    model._base_model = base_model

    return model


def unfreeze_for_finetuning(model: tf.keras.Model, fine_tune_from: int = FINE_TUNE_FROM) -> tf.keras.Model:
    """Unfreeze the top layers of the EfficientNetB0 base for Phase 2 fine-tuning.

    Args:
        model: The model returned by build_model().
        fine_tune_from: Layer index in the base model from which to unfreeze.
            EfficientNetB0 has 237 layers. Default 80 unfreezes ~66% of layers
            for deeper adaptation to the industrial defect domain.

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
        loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
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
