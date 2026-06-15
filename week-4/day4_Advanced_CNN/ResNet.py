import tensorflow as tf
from tensorflow.keras import layers, Model

inputs = layers.Input(shape=(32,32,3))

# Initial Conv
x = layers.Conv2D(32, (3,3), padding='same')(inputs)
x = layers.BatchNormalization()(x)
x = layers.ReLU()(x)

# Residual Block
shortcut = x

x = layers.Conv2D(32, (3,3), padding='same')(x)
x = layers.BatchNormalization()(x)
x = layers.ReLU()(x)

x = layers.Conv2D(32, (3,3), padding='same')(x)
x = layers.BatchNormalization()(x)

x = layers.Add()([x, shortcut])
x = layers.ReLU()(x)

# Classification Head
x = layers.GlobalAveragePooling2D()(x)
outputs = layers.Dense(10, activation='softmax')(x)

model = Model(inputs, outputs)

model.summary()