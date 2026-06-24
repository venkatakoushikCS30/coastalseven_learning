import pandas as pd
import numpy as np
import torch

from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
import evaluate

# =====================================
# Load Dataset
# =====================================

df = pd.read_csv("IMDB Dataset.csv")

# Convert sentiment labels
df["sentiment"] = df["sentiment"].map({
    "negative": 0,
    "positive": 1
})

# Optional: Use smaller subset for testing
# df = df.sample(5000, random_state=42)

# Convert to Hugging Face Dataset
dataset = Dataset.from_pandas(df)

# Train/Test Split
dataset = dataset.train_test_split(test_size=0.2)

# =====================================
# Load Tokenizer
# =====================================

tokenizer = DistilBertTokenizerFast.from_pretrained(
    "distilbert-base-uncased"
)

# =====================================
# Tokenization Function
# =====================================

def tokenize_function(examples):
    return tokenizer(
        examples["review"],
        padding="max_length",
        truncation=True,
        max_length=256
    )

tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True
)

# Rename label column
tokenized_dataset = tokenized_dataset.rename_column(
    "sentiment",
    "labels"
)

# Remove unnecessary columns
tokenized_dataset = tokenized_dataset.remove_columns(
    ["review"]
)

tokenized_dataset.set_format("torch")

# =====================================
# Load DistilBERT Model
# =====================================

model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=2
)

# =====================================
# Metric
# =====================================

accuracy_metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred

    predictions = np.argmax(
        logits,
        axis=-1
    )

    return accuracy_metric.compute(
        predictions=predictions,
        references=labels
    )

# =====================================
# Training Arguments
# =====================================

training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=2,
    weight_decay=0.01,
    load_best_model_at_end=True,
    report_to="none"
)

# =====================================
# Trainer
# =====================================

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    compute_metrics=compute_metrics
)

# =====================================
# Train Model
# =====================================

trainer.train()

# =====================================
# Evaluate
# =====================================

results = trainer.evaluate()

print("\nEvaluation Results:")
print(results)

# =====================================
# Save Model
# =====================================

trainer.save_model("./sentiment_model")
tokenizer.save_pretrained("./sentiment_model")

print("\nModel saved successfully!")

# =====================================
# Inference Example
# =====================================

text = "This movie was absolutely fantastic."

inputs = tokenizer(
    text,
    return_tensors="pt",
    truncation=True,
    padding=True
)

model.eval()

with torch.no_grad():
    outputs = model(**inputs)

prediction = torch.argmax(
    outputs.logits,
    dim=1
).item()

label = "Positive" if prediction == 1 else "Negative"

print("\nPrediction:")
print(text)
print("Sentiment:", label)