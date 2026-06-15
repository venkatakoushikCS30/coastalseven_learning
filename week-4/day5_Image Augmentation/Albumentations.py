import cv2
import albumentations as A
import matplotlib.pyplot as plt

# Read image
image = cv2.imread("cat.jpg")  # Replace with your image path
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Define augmentation pipeline
transform = A.Compose([
    A.HorizontalFlip(p=1.0),           # RandomFlip
    A.RandomCrop(
        width=200,
        height=200,
        p=1.0
    ),
    A.ColorJitter(
        brightness=0.3,
        contrast=0.3,
        saturation=0.3,
        hue=0.2,
        p=1.0
    ),
    A.CoarseDropout(                   # Cutout
        num_holes_range=(5, 10),
        hole_height_range=(20, 40),
        hole_width_range=(20, 40),
        fill=0,
        p=1.0
    )
])

# Apply augmentations
augmented = transform(image=image)
augmented_image = augmented["image"]

# Display Original and Augmented Images
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(image)
plt.title("Original")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(augmented_image)
plt.title("Augmented")
plt.axis("off")

plt.tight_layout()
plt.show()