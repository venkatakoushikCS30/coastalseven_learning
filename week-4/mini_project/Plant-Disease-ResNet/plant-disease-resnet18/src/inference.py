import json
import random
import yaml
from pathlib import Path
from typing import Tuple

import torch
import torch.nn.functional as F
from PIL import Image

from augmentations import get_val_transforms
from model import build_model
from dataset import build_file_list, stratified_split, _DEFAULT_DATA_ROOT

def predict_image(
    image: str | Path | Image.Image,
    model: torch.nn.Module,
    transform: torch.nn.Module,
    class_names: list[str],
    device: torch.device
) -> Tuple[str, float]:
    """
    Run inference on a single image and return the predicted class and confidence.
    """
    # 1. Load and prepare the image
    if isinstance(image, (str, Path)):
        img = Image.open(image).convert("RGB")
    else:
        img = image.convert("RGB")
        
    tensor = transform(img).unsqueeze(0).to(device)  # Add batch dimension [1, C, H, W]
    
    # 2. Predict
    model.eval()
    with torch.no_grad():
        outputs = model(tensor)
        probabilities = F.softmax(outputs, dim=1)
        
        confidence, predicted_idx = torch.max(probabilities, dim=1)
        
    class_idx = int(predicted_idx.item())
    conf_score = float(confidence.item())
    
    return class_names[class_idx], conf_score

def main() -> None:
    # 1. Load config and class names
    proj_root = Path(__file__).resolve().parent.parent
    with open(proj_root / "configs" / "hw_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    with open(proj_root / "configs" / "class_names.json", "r", encoding="utf-8") as f:
        class_names = json.load(f)
        
    device = torch.device(config["hyperparameters"]["device"])
    
    # 2. Build model and load weights
    model = build_model(num_classes=len(class_names), pretrained=False)
    checkpoint_path = proj_root / "models" / "best_finetune.pth"
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    
    # 3. Setup transform
    image_size = config["hyperparameters"]["image_size"]
    transform = get_val_transforms(image_size)
    
    # 4. Get a few random images from the test set
    samples = build_file_list(_DEFAULT_DATA_ROOT)
    _, _, test_samples = stratified_split(samples, seed=42)
    
    rng = random.Random(1234)
    random_test_samples = rng.sample(test_samples, 3)
    
    # 5. Run inference and print results
    print("=" * 60)
    print("  PHASE 7: INFERENCE TEST")
    print("=" * 60)
    
    for path, true_label_idx in random_test_samples:
        true_class = class_names[true_label_idx]
        pred_class, conf = predict_image(path, model, transform, class_names, device)
        
        print(f"Image: {Path(path).name}")
        print(f"True Class : {true_class}")
        print(f"Prediction : {pred_class} (Confidence: {conf*100:.1f}%)")
        print("-" * 60)

if __name__ == "__main__":
    main()
