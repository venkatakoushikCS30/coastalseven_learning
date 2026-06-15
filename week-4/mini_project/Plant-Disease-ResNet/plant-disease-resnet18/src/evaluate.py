import os
import json
import yaml
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from dataset import build_file_list, stratified_split, PlantVillageDataset, _DEFAULT_DATA_ROOT
from augmentations import get_val_transforms
from model import build_model

def main():
    # 1. Load config
    proj_root = Path(__file__).resolve().parent.parent
    with open(proj_root / "configs" / "hw_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    with open(proj_root / "configs" / "class_names.json", "r", encoding="utf-8") as f:
        class_names = json.load(f)
    
    device = torch.device(config["hyperparameters"]["device"])
    batch_size = config["hyperparameters"]["batch_size"]
    num_workers = config["hyperparameters"]["num_workers"]
    
    # 2. Dataset Test Split
    samples = build_file_list(_DEFAULT_DATA_ROOT)
    _, _, test_samples = stratified_split(samples, seed=42)
    
    test_transform = get_val_transforms(config["hyperparameters"]["image_size"])
    test_dataset = PlantVillageDataset(test_samples, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    
    # 3. Model
    model = build_model(num_classes=len(class_names), pretrained=False)
    
    # Load best finetuned weights
    checkpoint_path = proj_root / "models" / "best_finetune.pth"
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    
    # 4. Inference
    all_preds = []
    all_targets = []
    
    print(f"Evaluating on {len(test_dataset)} test samples...")
    with torch.no_grad():
        for i, (inputs, targets) in enumerate(test_loader):
            inputs = inputs.to(device)
            outputs = model(inputs)
            preds = torch.argmax(outputs, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.numpy())
            if i % 10 == 0:
                print(f"Processed batch {i}/{len(test_loader)}")
            
    # 5. Metrics
    report = classification_report(all_targets, all_preds, target_names=class_names)
    print("\nClassification Report:")
    print(report)
    
    # 6. Confusion Matrix
    cm = confusion_matrix(all_targets, all_preds)
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.title('Confusion Matrix on Test Set')
    plt.tight_layout()
    
    # Ensure results dir exists
    results_dir = proj_root / "results"
    results_dir.mkdir(exist_ok=True)
    
    plt.savefig(results_dir / "confusion_matrix.png", dpi=300)
    print(f"\nConfusion matrix saved to {results_dir / 'confusion_matrix.png'}")
    
    # Save report
    with open(results_dir / "classification_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()
