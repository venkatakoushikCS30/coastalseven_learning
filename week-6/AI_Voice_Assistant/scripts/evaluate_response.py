"""
Evaluation Script — Generates perplexity and sample outputs for the fine-tuned GPT-2 model.

IMPORTANT: Run this on Kaggle AFTER training the response model.
"""

import json
import torch
import math
from transformers import AutoTokenizer, AutoModelForCausalLM


PROMPT_TEMPLATE = "### Intent: {intent}\n### Customer: {user}\n### Agent:"


def compute_perplexity(model, tokenizer, texts, device, max_length=256):
    """Compute average perplexity over a list of text strings."""
    model.eval()
    total_loss = 0
    total_tokens = 0

    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length, padding=False)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        inputs["labels"] = inputs["input_ids"].clone()

        with torch.no_grad():
            outputs = model(**inputs)
            loss = outputs.loss
            num_tokens = inputs["input_ids"].shape[1]

        total_loss += loss.item() * num_tokens
        total_tokens += num_tokens

    avg_loss = total_loss / total_tokens
    perplexity = math.exp(avg_loss)
    return perplexity, avg_loss


def generate_sample(model, tokenizer, intent, user_text, device):
    """Generate a single response for display."""
    prompt = PROMPT_TEMPLATE.format(intent=intent, user=user_text)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the agent's response
    if "### Agent:" in full_output:
        response = full_output.split("### Agent:")[-1].strip()
    else:
        response = full_output[len(prompt):].strip()

    # Truncate at stop markers
    for marker in ["### Intent:", "### Customer:", "\n###", "\n\n"]:
        if marker in response:
            response = response.split(marker)[0].strip()

    return response


def main():
    # ── 1. Load Data ──
    data_path = "/kaggle/working/AI_Voice_Assistant/data/support_dialogues.json"
    with open(data_path, "r") as f:
        data = json.load(f)

    # Format as training strings for perplexity calculation
    formatted_texts = []
    for item in data:
        text = f"### Intent: {item['intent']}\n### Customer: {item['user']}\n### Agent: {item['response']}"
        formatted_texts.append(text)

    # ── 2. Load Model ──
    model_path = "/kaggle/working/response_finetuned"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # ── 3. Perplexity ──
    print("=" * 60)
    print("       GPT-2 RESPONSE MODEL — EVALUATION METRICS")
    print("=" * 60)

    perplexity, avg_loss = compute_perplexity(model, tokenizer, formatted_texts, device)
    print(f"\n  Average Cross-Entropy Loss:  {avg_loss:.4f}")
    print(f"  Perplexity:                  {perplexity:.2f}")
    print(f"\n  (Lower perplexity = model is more confident about the training data)")
    print(f"  (A well-fine-tuned small GPT-2 on 50 examples typically gets perplexity 1-10)")

    # ── 4. Sample Generations ──
    test_queries = [
        ("track_order", "Where is my order?"),
        ("refund_request", "I want to return this product"),
        ("speak_to_human", "Can I talk to a real person?"),
        ("product_info", "What colors does this come in?"),
        ("cancel_order", "I want to cancel my purchase"),
    ]

    print("\n" + "=" * 60)
    print("       SAMPLE GENERATIONS (one per intent)")
    print("=" * 60)

    for intent, query in test_queries:
        response = generate_sample(model, tokenizer, intent, query, device)
        print(f"\n  Intent:   {intent}")
        print(f"  Customer: {query}")
        print(f"  Agent:    {response}")
        print(f"  {'─' * 50}")


if __name__ == "__main__":
    main()
