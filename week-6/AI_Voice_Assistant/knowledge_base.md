# Knowledge Base — AI Voice Assistant

## Architecture
```
Microphone → Whisper STT → DistilBERT Intent → GPT-2 Response → Kokoro TTS → Audio Playback
     ↑                                                                          ↓
     └──────────────────────── Gradio UI ────────────────────────────────────────┘
```

## Selected Stack (Phase 0 Research → Updated After Pivot)

| Component         | Library / Model                        | Version / Variant          | Status         |
|-------------------|----------------------------------------|----------------------------|----------------|
| UI                | Gradio                                 | ≥5.x                      | ✅ Integrated  |
| STT               | faster-whisper (CTranslate2 backend)   | latest; model: base        | ✅ Integrated  |
| Intent Extraction | DistilBERT (HuggingFace transformers)  | distilbert-base-uncased     | ✅ Fine-Tuned  |
| Response Gen      | GPT-2 (HuggingFace)                    | gpt2 (124M)                | ✅ Fine-Tuned  |
| TTS               | Kokoro-82M                             | kokoro (pip)               | ✅ Integrated  |
| Audio I/O         | librosa                                | latest                     | ✅ Integrated  |

## Target Environment
- **GPU**: Kaggle — NVIDIA T4 (16GB VRAM) or P100 (16GB VRAM)
- **CUDA**: Pre-installed on Kaggle
- Heavy compute phases (fine-tuning) are run as Kaggle notebook cells

## Dependencies
```
gradio, faster-whisper, transformers, torch, kokoro, librosa, soundfile, numpy, datasets
```

## Known Issues / Risks
- Kokoro requires `espeak-ng` system dependency (pre-install on Kaggle via `apt-get`).
- GPU (T4/P100) available on Kaggle — no CPU constraint concerns.
- Kaggle `transformers` version is bleeding-edge (4.45+): use `eval_strategy` not `evaluation_strategy`, and `processing_class` not `tokenizer` in Trainer.
- Kaggle wipes `/kaggle/working/` on session restart — fine-tuned models must be re-trained or uploaded as Kaggle Datasets.
- `config.py` uses relative paths locally (`models/intent_finetuned`); must be patched to absolute paths on Kaggle.

## Customer Support Domain (Pivot)
- **Domain**: E-commerce customer support
- **Intent Labels**: `cancel_order`, `product_info`, `refund_request`, `speak_to_human`, `track_order`
- **Intent Dataset**: `data/support_intents.json` — 50 synthetic examples (10 per class)
- **Intent Training Script**: `scripts/train_intent.py` — uses HuggingFace `Trainer` API
- **Dialogue Dataset**: `data/support_dialogues.json` — 50 synthetic dialogues (10 per intent) with professional agent responses
- **Response Training Script**: `scripts/train_response.py` — GPT-2 Causal LM fine-tuning with `DataCollatorForLanguageModeling`
- **Prompt Template** *(critical — must match between training and inference)*: `### Intent: {intent}\n### Customer: {text}\n### Agent:`

## Phase Log
| Phase   | Status    | Notes                                      |
|---------|-----------|--------------------------------------------|
| 0       | ✅ Done   | Research complete, stack selected           |
| 1       | ✅ Done   | Scaffolding, config, Gradio shell           |
| 2       | ✅ Done   | STT via faster-whisper + librosa            |
| 3       | ✅ Done   | Intent via DistilBERT zero-shot (initial)   |
| 4       | ✅ Done   | Response via GPT-2 text-generation          |
| 5       | ✅ Done   | TTS synthesis via Kokoro-82M               |
| 6       | ✅ Done   | Pipeline Integration & Error Bounds         |
| 7       | ✅ Done   | Gradio UI Polish & Autoplay                |
| P1      | ✅ Done   | DistilBERT Fine-Tuned for Customer Support |
| P2      | ✅ Done  | GPT-2 Fine-Tuned for Support Dialogues     |
| P3      | ✅ Done   | Final Integration & Code Cleanup           |
