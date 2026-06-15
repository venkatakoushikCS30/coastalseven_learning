import matplotlib.pyplot as plt

train_losses = [1.2, 0.9, 0.7, 0.5, 0.3, 0.2]
val_losses   = [1.1, 0.8, 0.6, 0.7, 0.9, 1.1]

train_accs = [55, 65, 75, 85, 92, 98]
val_accs   = [54, 63, 73, 76, 74, 72]

# Loss Curve
plt.figure(figsize=(10,4))

plt.subplot(1,2,1)
plt.plot(train_losses, marker='o', label='Train')
plt.plot(val_losses, marker='o', label='Validation')
plt.title("Loss Curve")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()

# Accuracy Curve
plt.subplot(1,2,2)
plt.plot(train_accs, marker='o', label='Train')
plt.plot(val_accs, marker='o', label='Validation')
plt.title("Accuracy Curve")
plt.xlabel("Epoch")
plt.ylabel("Accuracy (%)")
plt.legend()

plt.tight_layout()
plt.show()