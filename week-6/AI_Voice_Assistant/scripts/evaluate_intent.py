"""
Evaluation Script — Generates classification metrics for the fine-tuned DistilBERT model.
Outputs: Accuracy, Precision, Recall, F1-Score, and a per-class Classification Report.

IMPORTANT: Run this on Kaggle AFTER training the intent model.
"""

import json
import torch
import numpy as np
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)


def main():
    # ── 1. Load Dataset ──
    data_path = "/kaggle/working/AI_Voice_Assistant/data/support_intents.json"
    with open(data_path, "r") as f:
        data = json.load(f)

    labels_list = sorted(list(set([item["label"] for item in data])))
    label2id = {label: i for i, label in enumerate(labels_list)}
    id2label = {i: label for i, label in enumerate(labels_list)}

    texts = [item["text"] for item in data]
    y_true_ids = [label2id[item["label"]] for item in data]

    # Use the SAME split as training (seed=42, test_size=0.2)
    dataset = Dataset.from_dict({"text": texts, "label": y_true_ids})
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    test_dataset = dataset["test"]

    print(f"Test set size: {len(test_dataset)} examples")
    print(f"Classes: {labels_list}")
    print("-" * 60)

    # ── 2. Load Fine-Tuned Model ──
    model_path = "/kaggle/working/intent_finetuned"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    # ── 3. Run Inference on Test Set ──
    y_true = []
    y_pred = []

    for example in test_dataset:
        text = example["text"]
        true_label = example["label"]

        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=64, padding="max_length")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_id = torch.argmax(logits, dim=-1).item()

        y_true.append(true_label)
        y_pred.append(predicted_id)

    # ── 4. Compute Metrics ──
    accuracy = accuracy_score(y_true, y_pred)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

    print("=" * 60)
    print("       INTENT CLASSIFICATION — EVALUATION METRICS")
    print("=" * 60)
    print(f"\n  Accuracy:           {accuracy:.4f}  ({accuracy*100:.1f}%)")
    print(f"\n  Macro Precision:    {precision_macro:.4f}")
    print(f"  Macro Recall:       {recall_macro:.4f}")
    print(f"  Macro F1-Score:     {f1_macro:.4f}")
    print(f"\n  Weighted Precision: {precision_weighted:.4f}")
    print(f"  Weighted Recall:    {recall_weighted:.4f}")
    print(f"  Weighted F1-Score:  {f1_weighted:.4f}")

    print("\n" + "=" * 60)
    print("       PER-CLASS CLASSIFICATION REPORT")
    print("=" * 60)
    target_names = [id2label[i] for i in range(len(labels_list))]
    print(classification_report(y_true, y_pred, target_names=target_names, zero_division=0))

    print("=" * 60)
    print("       CONFUSION MATRIX")
    print("=" * 60)
    cm = confusion_matrix(y_true, y_pred)
    print(f"\nLabels: {target_names}")
    print(cm)


if __name__ == "__main__":
    main()
