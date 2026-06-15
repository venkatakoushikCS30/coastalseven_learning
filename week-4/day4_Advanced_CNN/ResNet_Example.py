import torch
import torch.nn as nn
import torch.optim as optim

from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

# ==========================================
# Device Configuration
# ==========================================
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using Device:", device)

# ==========================================
# Hyperparameters
# ==========================================
BATCH_SIZE = 32
EPOCHS = 5
LEARNING_RATE = 0.001
NUM_CLASSES = 5

# ==========================================
# Data Transformations
# ==========================================
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ==========================================
# Load Dataset
# ==========================================
train_dataset = datasets.ImageFolder(
    root="dataset/train",
    transform=train_transform
)

val_dataset = datasets.ImageFolder(
    root="dataset/val",
    transform=val_transform
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

print("Classes:", train_dataset.classes)

# ==========================================
# Load Pretrained ResNet18
# ==========================================
model = models.resnet18(
    weights=models.ResNet18_Weights.DEFAULT
)

# Freeze all pretrained layers
for param in model.parameters():
    param.requires_grad = False

# Replace final classifier
num_features = model.fc.in_features

model.fc = nn.Linear(
    num_features,
    NUM_CLASSES
)

model = model.to(device)

# ==========================================
# Loss Function & Optimizer
# ==========================================
criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.fc.parameters(),
    lr=LEARNING_RATE
)

# ==========================================
# Training Loop
# ==========================================
for epoch in range(EPOCHS):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)

        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

        _, predicted = torch.max(outputs, 1)

        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    train_acc = 100 * correct / total

    # ======================================
    # Validation
    # ======================================
    model.eval()

    val_correct = 0
    val_total = 0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            _, predicted = torch.max(outputs, 1)

            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()

    val_acc = 100 * val_correct / val_total

    print(
        f"Epoch [{epoch+1}/{EPOCHS}] | "
        f"Loss: {running_loss/len(train_loader):.4f} | "
        f"Train Acc: {train_acc:.2f}% | "
        f"Val Acc: {val_acc:.2f}%"
    )

print("\nTraining Complete!")

# ==========================================
# Save Model
# ==========================================
torch.save(
    model.state_dict(),
    "resnet18_custom_5class.pth"
)

print("Model Saved Successfully!")

# ==========================================
# Predict Single Image
# ==========================================
from PIL import Image

image_path = "test.jpg"

image = Image.open(image_path).convert("RGB")

image = val_transform(image)

image = image.unsqueeze(0).to(device)

model.eval()

with torch.no_grad():

    output = model(image)

    predicted_class = torch.argmax(
        output,
        dim=1
    )

print(
    "Prediction:",
    train_dataset.classes[
        predicted_class.item()
    ]
)