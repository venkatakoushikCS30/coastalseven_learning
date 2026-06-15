import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

# Load image
image = tf.keras.utils.load_img(
    " ",
    target_size=(128, 128)
)

image = tf.keras.utils.img_to_array(image)
image = image / 255.0
image = np.expand_dims(image, axis=0)

# Simple CNN model
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(
        filters=8,
        kernel_size=(3, 3),
        activation='relu',
        input_shape=(128, 128, 3)
    )
])

# Generate feature maps
feature_maps = model.predict(image)

print("Feature map shape:", feature_maps.shape)
# Output: (1, 126, 126, 8)

# Visualize feature maps
fig, axes = plt.subplots(2, 4, figsize=(10, 5))

for i, ax in enumerate(axes.flat):
    ax.imshow(feature_maps[0, :, :, i], cmap='gray')
    ax.set_title(f'Filter {i+1}')
    ax.axis('off')

plt.tight_layout()
plt.show()