import json
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src import config

def check_model_exists() -> bool:
    """Check if the model and tokenizer exist in the local directory."""
    required_files = ["config.json", "tokenizer_config.json"]
    # At least one model weight format (safetensors or bin) should be present
    weight_extensions = [".safetensors", ".bin"]
    
    if not config.MODEL_PATH.exists():
        return False
        
    files = [f.name for f in config.MODEL_PATH.iterdir() if f.is_file()]
    
    has_config = all(req in files for req in required_files)
    has_weights = any(any(f.endswith(ext) for ext in weight_extensions) for f in files)
    
    return has_config and has_weights

def load_label_mappings():
    """Load id2label and label2id from local processed folder."""
    if not config.LABEL_MAPS_PATH.exists():
        print(f"Error: Label maps file not found at {config.LABEL_MAPS_PATH}")
        sys.exit(1)
        
    with open(config.LABEL_MAPS_PATH, "r") as f:
        label_maps = json.load(f)
        
    # Ensure keys in id2label are integers
    id2label = {int(k): v for k, v in label_maps["id2label"].items()}
    label2id = {k: int(v) for k, v in label_maps["label2id"].items()}
    return id2label, label2id

def evaluate_model():
    # 1. Verification of local model
    if not check_model_exists():
        print("=" * 80)
        print("WARNING: LOCAL MODEL FILES NOT FOUND!")
        print("=" * 80)
        print(f"Please download the trained model files from Kaggle and place them in:")
        print(f"  {config.MODEL_PATH.absolute()}")
        print("\nRequired files to copy:")
        print("  - config.json")
        print("  - tokenizer_config.json")
        print("  - model.safetensors (or pytorch_model.bin)")
        print("  - vocab.txt")
        print("  - tokenizer.json")
        print("  - special_tokens_map.json")
        print("=" * 80)
        return

    print("Loading model and tokenizer...")
    id2label, label2id = load_label_mappings()
    num_labels = len(id2label)

    # Load model and tokenizer from local folder
    try:
        tokenizer = AutoTokenizer.from_pretrained(config.MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(config.MODEL_PATH)
    except Exception as e:
        print(f"Error loading model from {config.MODEL_PATH}: {e}")
        return

    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print(f"Model successfully loaded on: {device}")

    # 2. Load test dataset
    if not config.TEST_PATH.exists():
        print(f"Error: Test dataset not found at {config.TEST_PATH}")
        return
        
    test_df = pd.read_csv(config.TEST_PATH)
    print(f"Loaded test dataset ({len(test_df)} samples).")

    texts = test_df["text"].tolist()
    y_true = test_df["label_id"].astype(int).tolist()

    # 3. Perform batch inference
    batch_size = 16
    y_pred = []

    print("Running evaluation inference...")
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        # Tokenize inputs
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=config.MAX_LENGTH,
            return_tensors="pt"
        )
        
        # Move inputs to device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits.cpu().numpy()
            preds = np.argmax(logits, axis=-1)
            y_pred.extend(preds.tolist())

    # 4. Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    target_names = [id2label[i] for i in range(num_labels)]
    
    # Classification report as dict and text
    report_dict = classification_report(y_true, y_pred, target_names=target_names, output_dict=True, zero_division=0)
    report_text = classification_report(y_true, y_pred, target_names=target_names, zero_division=0)
    
    print("\n" + "=" * 50)
    print("EVALUATION RESULT")
    print("=" * 50)
    print(f"Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:\n")
    print(report_text)
    print("=" * 50)

    # Save evaluation report as JSON
    report_output = {
        "accuracy": accuracy,
        "classification_report": report_dict,
        "model_name": config.MODEL_NAME,
        "test_samples": len(test_df)
    }
    
    with open(config.EVAL_REPORT_PATH, "w") as f:
        json.dump(report_output, f, indent=4)
    print(f"Saved evaluation report to: {config.EVAL_REPORT_PATH}")

    # 5. Plot and save Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm, 
        annot=True, 
        fmt="d", 
        cmap="Blues", 
        xticklabels=target_names, 
        yticklabels=target_names
    )
    plt.title("Confusion Matrix - FAQ Intent Classification")
    plt.ylabel("True Intent")
    plt.xlabel("Predicted Intent")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    plt.savefig(config.CONFUSION_MATRIX_PATH, dpi=300)
    plt.close()
    print(f"Saved confusion matrix plot to: {config.CONFUSION_MATRIX_PATH}")

if __name__ == "__main__":
    evaluate_model()
