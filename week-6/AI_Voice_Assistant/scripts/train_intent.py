"""
DistilBERT Fine-tuning Script for Customer Support Intents.
This script trains a DistilBERT sequence classification head on custom data.

IMPORTANT: Run this script on Kaggle with a GPU (T4/P100).
"""

import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

def load_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    
    # Extract unique labels
    labels = sorted(list(set([item["label"] for item in data])))
    label2id = {label: i for i, label in enumerate(labels)}
    id2label = {i: label for i, label in enumerate(labels)}
    
    # Format for Hugging Face datasets
    texts = [item["text"] for item in data]
    y = [label2id[item["label"]] for item in data]
    
    return texts, y, label2id, id2label

def main():
    print("[1/5] Loading custom dataset...")
    data_path = "../data/support_intents.json"
    texts, labels, label2id, id2label = load_data(data_path)
    
    # Create HuggingFace Dataset
    dataset = Dataset.from_dict({"text": texts, "label": labels})
    
    # Split into train/test
    # Since our synthetic dataset is tiny (50 rows), we'll train on 80% and test on 20%
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = dataset["train"]
    test_dataset = dataset["test"]
    
    print(f"[2/5] Initializing Tokenizer... (Found {len(label2id)} classes)")
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=64)
    
    print("[3/5] Tokenizing dataset...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_test = test_dataset.map(tokenize_function, batched=True)
    
    print("[4/5] Loading DistilBERT Model...")
    # We specify num_labels so the classification head is initialized correctly
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=len(label2id),
        id2label=id2label,
        label2id=label2id
    )
    
    # Check GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on device: {device.upper()}")
    model.to(device)
    
    print("[5/5] Starting Fine-tuning...")
    training_args = TrainingArguments(
        output_dir="../models/intent_finetuned",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=5,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_dir="./logs",
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        processing_class=tokenizer,
    )
    
    trainer.train()
    
    print("Saving fine-tuned model...")
    trainer.save_model("../models/intent_finetuned")
    print("Done! The model is saved at: models/intent_finetuned")

if __name__ == "__main__":
    main()
