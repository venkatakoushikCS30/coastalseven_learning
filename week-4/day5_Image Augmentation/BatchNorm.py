import tensorflow as tf
from tensorflow.keras import layers, models

model = models.Sequential([

    # Convolution Layer
    layers.Conv2D(
        filters=32,
        kernel_size=(3,3),
        padding='same',
        input_shape=(32,32,3)
    ),

    # Batch Normalization
    layers.BatchNormalization(),

    # Activation
    layers.ReLU(),

    # Pooling
    layers.MaxPooling2D((2,2)),

    # Flatten
    layers.Flatten(),

    # Dense Layer
    layers.Dense(128),

    # Batch Normalization
    layers.BatchNormalization(),

    # Activation
    layers.ReLU(),

    # Output Layer
    layers.Dense(10, activation='softmax')
])

model.summary()