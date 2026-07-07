"""
GPT-2 Supervised Fine-Tuning Script for Customer Support Dialogues.
Trains GPT-2 to generate professional customer support responses.

IMPORTANT: Run this script on Kaggle with a GPU (T4/P100).
"""

import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)


# ── Prompt format (must match inference in modules/response.py) ──
PROMPT_TEMPLATE = """### Intent: {intent}
### Customer: {user}
### Agent: {response}"""


def load_data(file_path):
    """Load dialogue JSON and format each example as a single training string."""
    with open(file_path, "r") as f:
        data = json.load(f)

    formatted = []
    for item in data:
        text = PROMPT_TEMPLATE.format(
            intent=item["intent"],
            user=item["user"],
            response=item["response"]
        )
        formatted.append({"text": text})

    return formatted


def main():
    print("[1/5] Loading dialogue dataset...")
    data_path = "../data/support_dialogues.json"
    formatted_data = load_data(data_path)
    dataset = Dataset.from_list(formatted_data)

    # Split into train/test
    dataset = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = dataset["train"]
    test_dataset = dataset["test"]
    print(f"  Train: {len(train_dataset)} examples, Test: {len(test_dataset)} examples")

    print("[2/5] Loading GPT-2 Tokenizer...")
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # GPT-2 has no pad token by default — set it to eos_token
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_function(examples):
        tokens = tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=256
        )
        # For causal LM, labels = input_ids (the model learns to predict next token)
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens

    print("[3/5] Tokenizing dataset...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True, remove_columns=["text"])
    tokenized_test = test_dataset.map(tokenize_function, batched=True, remove_columns=["text"])

    print("[4/5] Loading GPT-2 Model...")
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.config.pad_token_id = tokenizer.eos_token_id

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Training on device: {device.upper()}")
    model.to(device)

    print("[5/5] Starting Fine-tuning...")
    training_args = TrainingArguments(
        output_dir="../models/response_finetuned",
        learning_rate=5e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=10,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=5,
        fp16=torch.cuda.is_available(),
        logging_dir="./logs",
    )

    # Data collator handles dynamic padding for causal LM
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # We are doing Causal LM, NOT Masked LM
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        data_collator=data_collator,
        processing_class=tokenizer,
    )

    trainer.train()

    print("Saving fine-tuned model...")
    trainer.save_model("../models/response_finetuned")
    tokenizer.save_pretrained("../models/response_finetuned")
    print("Done! The model is saved at: models/response_finetuned")


if __name__ == "__main__":
    main()
