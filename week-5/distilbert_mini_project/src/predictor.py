import json
import sys
import argparse
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path

from src import config

class IntentPredictor:
    def __init__(self, model_path: Path = None):
        """Initialize the predictor by loading the model and tokenizer."""
        self.model_path = model_path or config.MODEL_PATH
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Verify model directory and files exist
        if not self._check_model_exists():
            print(f"Error: Model files not found at '{self.model_path}'.", file=sys.stderr)
            print("Please make sure you have downloaded the fine-tuned model from Kaggle.", file=sys.stderr)
            sys.exit(1)

        print(f"Loading tokenizer and model from {self.model_path}...", file=sys.stderr)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Error initializing model/tokenizer: {e}", file=sys.stderr)
            sys.exit(1)

        # Load label map config
        self.id2label, self.label2id = self._load_label_mappings()
        print(f"Predictor successfully initialized on device: {self.device}", file=sys.stderr)

    def _check_model_exists(self) -> bool:
        """Check if critical model files exist locally."""
        required_files = ["config.json", "tokenizer_config.json"]
        if not self.model_path.exists():
            return False
        files = [f.name for f in self.model_path.iterdir() if f.is_file()]
        has_config = all(req in files for req in required_files)
        has_weights = any(f.endswith(".safetensors") or f.endswith(".bin") for f in files)
        return has_config and has_weights

    def _load_label_mappings(self):
        """Load label maps from config JSON inside model directory or processed data folder."""
        # Check model directory first
        model_label_map = self.model_path / "label_maps.json"
        # Fallback to dataset directory
        dataset_label_map = config.LABEL_MAPS_PATH
        
        path_to_load = model_label_map if model_label_map.exists() else dataset_label_map
        
        if not path_to_load.exists():
            # If label_maps.json doesn't exist, we can use the model config's id2label
            if hasattr(self.model.config, "id2label") and self.model.config.id2label:
                id2label = {int(k): v for k, v in self.model.config.id2label.items()}
                label2id = {v: int(k) for k, v in id2label.items()}
                return id2label, label2id
            else:
                print("Error: Could not find label_maps.json or id2label in model config.", file=sys.stderr)
                sys.exit(1)

        with open(path_to_load, "r") as f:
            label_maps = json.load(f)
            
        id2label = {int(k): v for k, v in label_maps["id2label"].items()}
        label2id = {k: int(v) for k, v in label_maps["label2id"].items()}
        return id2label, label2id

    def predict(self, text: str):
        """Predict intent class and probabilities for the input query."""
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a non-empty string.")

        text = text.strip()
        
        # Tokenize text
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=config.MAX_LENGTH,
            return_tensors="pt"
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1).cpu().numpy()[0]

        # Get best prediction
        pred_idx = int(np.argmax(probabilities))
        pred_label = self.id2label[pred_idx]
        confidence = float(probabilities[pred_idx])

        # Prepare full probability map (sorted descending)
        all_probs = {self.id2label[i]: float(probabilities[i]) for i in range(len(probabilities))}
        sorted_probs = dict(sorted(all_probs.items(), key=lambda x: x[1], reverse=True))

        return {
            "text": text,
            "intent": pred_label,
            "label_id": pred_idx,
            "confidence": confidence,
            "probabilities": sorted_probs
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FAQ Intent Prediction Module")
    parser.add_argument("text", type=str, nargs="?", help="Text query to predict intent for")
    args = parser.parse_args()

    # If no argument is passed, run interactively
    if not args.text:
        print("Starting interactive predictor. Type 'exit' or 'quit' to stop.")
        try:
            predictor = IntentPredictor()
            while True:
                user_input = input("\nEnter query: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input.strip():
                    continue
                try:
                    result = predictor.predict(user_input)
                    print(f"Predicted Intent: {result['intent']} (Confidence: {result['confidence']:.4f})")
                    print("Top 3 Intent Probabilities:")
                    for idx, (intent, prob) in enumerate(list(result['probabilities'].items())[:3]):
                        print(f"  {idx+1}. {intent}: {prob:.4f}")
                except Exception as e:
                    print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
    else:
        # Single query mode
        predictor = IntentPredictor()
        try:
            result = predictor.predict(args.text)
            print(json.dumps(result, indent=4))
        except Exception as e:
            print(f"Error during prediction: {e}", file=sys.stderr)
            sys.exit(1)
