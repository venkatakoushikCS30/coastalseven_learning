# Project Tracker — AI Voice Assistant

## ✅ Completed Phases (Original Pipeline)
- **Phase 0**: Research — Library/model selection for all pipeline components
- **Phase 1**: Project Setup & Scaffolding — Directory structure, deps, config, Gradio shell
- **Phase 2**: STT Module — faster-whisper integration with librosa preprocessing
- **Phase 3**: Intent Extraction — DistilBERT zero-shot classification (later replaced in Pivot Phase 1)
- **Phase 4**: Response Generation — Autoregressive GPT-2 text-generation pipeline
- **Phase 5**: TTS Module — Kokoro-82M synthesis with KPipeline + numpy concatenation
- **Phase 6**: Pipeline Integration — Error handling, fail-fast returns, safe dict access
- **Phase 7**: Gradio UI Polish — Centered HTML header, autoplay TTS, accordion for technical details, clear button

## 🚀 MAJOR PIVOT: Customer Support Agent
The project shifted from a generic voice assistant to a specialized **e-commerce customer support agent**.
This required generating synthetic data and explicitly fine-tuning the underlying neural networks.

### Pivot Roadmap
- **Pivot Phase 1 (Intent Fine-Tuning)** `[✅ COMPLETED]`
  - Generated `data/support_intents.json` — 50 synthetic e-commerce queries mapped to 5 intents
  - Wrote `scripts/train_intent.py` — Hugging Face `Trainer` script for Kaggle GPU
  - Trained DistilBERT for 5 epochs on Kaggle T4 GPU (training time: ~9 seconds)
  - Refactored `modules/intent.py` from `zero-shot-classification` → `text-classification`
  - Updated `config.py` to point to local fine-tuned weights
  - **Intents**: `track_order`, `refund_request`, `speak_to_human`, `product_info`, `cancel_order`

- **Pivot Phase 2 (Response Fine-Tuning)** `[✅ COMPLETED]`
  - Generated `data/support_dialogues.json` — 50 synthetic customer support dialogues (10 per intent) with professional agent responses
  - Wrote `scripts/train_response.py` — GPT-2 Causal LM fine-tuning script using HuggingFace Trainer with DataCollatorForLanguageModeling
  - Refactored `modules/response.py` — Changed prompt format to `### Intent: {intent}\n### Customer: {text}\n### Agent:` to match training data. Added stop-marker truncation to prevent multi-turn hallucination.
  - Updated `config.py` — Changed `RESPONSE_MODEL_NAME` from `"gpt2"` to `"models/response_finetuned"`

- **Pivot Phase 3 (Final Integration & Testing)** `[✅ COMPLETED]`
  - Cleaned up all outdated comments/docstrings across `app.py` and `modules/intent.py`
  - Updated UI header to "AI Customer Support Agent"
  - Updated footer to reflect fine-tuned model status
  - All modules verified: `stt.py`, `intent.py`, `response.py`, `tts.py`

## 🔄 Current Phase
- **PROJECT COMPLETE** ✅ — All phases done. User needs to run both training scripts on Kaggle, then launch `app.py`.

## 📁 Current File Inventory
| File | Purpose | Last Modified |
|------|---------|---------------|
| `app.py` | Gradio UI + pipeline orchestrator | Phase 7 |
| `config.py` | Central config (models, hyperparams, device) | Pivot Phase 2 |
| `requirements.txt` | pip dependencies | Phase 1 |
| `modules/stt.py` | SpeechToText class (faster-whisper + librosa) | Phase 2 |
| `modules/intent.py` | IntentClassifier class (fine-tuned DistilBERT) | Pivot Phase 1 |
| `modules/response.py` | ResponseGenerator class (fine-tuned GPT-2) | Pivot Phase 2 |
| `modules/tts.py` | TextToSpeech class (Kokoro-82M) | Phase 5 |
| `data/intents.json` | Original 9-class intent dataset (72 examples) | Phase 1 |
| `data/support_intents.json` | Customer support dataset (50 examples, 5 classes) | Pivot Phase 1 |
| `data/support_dialogues.json` | Customer support dialogue dataset (50 dialogues, 10 per intent) | Pivot Phase 2 |
| `scripts/train_intent.py` | DistilBERT fine-tuning script for Kaggle GPU | Pivot Phase 1 |
| `scripts/train_response.py` | GPT-2 Causal LM fine-tuning script for Kaggle GPU | Pivot Phase 2 |
| `knowledge_base.md` | Architecture decisions log | Pivot Phase 2 |
| `project_tracker.md` | This file | Pivot Phase 2 |
| `project_details.md` | Deep-dive documentation + viva questions (Q1–Q32) | Pivot Phase 2 |
| `README.md` | Project documentation (all phases) | Pivot Phase 2 |

## ⚠️ Handoff Notes for Next Agent
1. **Kaggle Path Issue**: When running on Kaggle, `config.py` must be patched to use absolute paths (e.g., `/kaggle/working/intent_finetuned`). The local config uses relative paths (`models/intent_finetuned`).
2. **Transformers Version**: Kaggle has bleeding-edge `transformers` (4.45+). Use `eval_strategy` (not `evaluation_strategy`) and `processing_class` (not `tokenizer`) in `Trainer`/`TrainingArguments`.
3. **espeak-ng**: Kokoro TTS requires `espeak-ng`. Install on Kaggle via `!apt-get install -y espeak-ng`.
4. **Gradio Share**: `app.py` uses `share=True` so Kaggle generates a public `.gradio.live` URL.
