# Gemma: Google's Open-Source LLM Guide

---

## 1. What is Gemma?

Open-source LLM series by Google DeepMind. Lightweight alternative to Gemini based on similar technologies.

**Developer:** Google DeepMind | **Latest:** Gemma 4 (April 2, 2026)

---

## 2. Gemma Model Versions

| Version | Release | Details |
|---------|---------|---------|
| Gemma 1 | Feb 2024 | 2B, 7B parameters |
| Gemma 2 | Jun 2024 | Improved efficiency |
| Gemma 3 | Mar 2025 | 1B-27B, 128k context, multimodal, 140+ languages |
| Gemma 4 | Apr 2026 | E2B, E4B, 26B A4B, 31B Dense |

**Gemma 4 Use Cases:**
- E2B, E4B: Mobile, IoT, edge devices
- 26B: Consumer GPUs
- 31B: Frontier-level performance

---

## 3. Key Capabilities

- Reasoning with step-by-step thinking mode
- Multimodal: Text, Image (variable aspect ratio), Video, Audio
- Context: 128K tokens (E2B/E4B), 256K tokens (26B/31B)
- Image understanding: Object detection, OCR, chart comprehension, handwriting
- Video understanding: Frame-by-frame analysis
- Function calling: Native tool use for agentic workflows
- Enhanced coding capabilities

---

## 4. Performance

Gemma-3-4B beats Gemma-2-27B. Gemma-4-31B ranks #3 on Arena AI text leaderboard.

---

## 5. Steps to Run Gemma Through API

### Step 1: Get API Key
Visit https://aistudio.google.com → Sign in → Click "Get API Key" → Copy and store safely

### Step 2: Install Libraries
```bash
pip install google-generativeai google-genai
```

### Step 3: Set Environment Variable
```bash
export GEMINI_API_KEY='your_api_key_here'
```

### Step 4: Basic Usage
```python
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemma-4-26b-a4b-it")
response = model.generate_content("Your prompt here")
print(response.text)
```

### Step 5: Multi-turn Conversation
```python
from google import genai
client = genai.Client(api_key="YOUR_API_KEY")
chat = client.chats.create(model="gemma-4-26b-a4b-it")
response = chat.send_message("First message")
response = chat.send_message("Follow-up message")
```

### Step 6: Image Processing
Send images with text to the model for analysis.

### Step 7: Search Grounding
Add `tools=[{"google_search": {}}]` to enable web search for responses.

### Step 8: Function Calling
Define function declarations for tool use and agentic workflows.

### Step 9: Thinking Mode (Advanced)
Enable with `thinking={"type": "enabled", "budget_tokens": 10000}` for complex reasoning.

### Step 10: System Instructions
Pass `system_instruction` parameter to customize model behavior.

## 6. Available Models on Gemini API

- `gemma-4-26b-a4b-it` - 26B instruction-tuned
- `gemma-4-31b-it` - 31B instruction-tuned
- `gemma-3-27b-it` - 27B instruction-tuned (Gemma 3)

---

## 7. Pricing

**Free Tier:** Learning, testing, demos, small projects. No subscription required.

**Paid Tier:** Production use, higher limits, dedicated support.

---

## 8. Security & Best Practices

- Use environment variables for API keys (never hardcode)
- Restrict API keys to Gemini API only in AI Studio
- Rotate keys regularly
- Use smaller models (E2B/E4B) for cost optimization
- Implement exponential backoff for rate limits

---

## 9. Resources

- Google AI Studio: https://aistudio.google.com
- API Docs: https://ai.google.dev
- Model Card: https://ai.google.dev/gemma/docs/core/model_card_4