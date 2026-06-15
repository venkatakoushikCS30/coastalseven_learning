import torch
import torch.nn as nn
import torchvision.models as models

# Load pretrained model
model = models.resnet18(
    weights=models.ResNet18_Weights.DEFAULT
)

# Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# Replace classifier
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 2)

# Optimizer only for classifier
optimizer = torch.optim.Adam(
    model.fc.parameters(),
    lr=0.001
)

print(model)