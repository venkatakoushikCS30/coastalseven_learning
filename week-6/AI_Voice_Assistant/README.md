# AI Voice Assistant

End-to-end voice assistant: **Microphone → STT → Intent Extraction → Response Generation → TTS → Audio Playback**, powered entirely by open-source models with a Gradio web UI.

## Phase 0 — Research & Library Selection

### Operation
Researched the 2025–2026 open-source ecosystem for each pipeline component. Selected the optimal library/model for each stage based on: performance, ease of integration, licensing, and hardware requirements.

### Files Changed
- `knowledge_base.md` — Created with architecture + selected stack
- `project_tracker.md` — Created with phase roadmap
- `README.md` — This file
- `project_details.md` — Fresher-friendly deep-dive documentation

### Technical Details

#### Selected Stack Summary

| Component            | Selected                     | Alternatives Considered                    |
|----------------------|------------------------------|--------------------------------------------|
| **UI**               | Gradio ≥5.x                 | Streamlit, Flask                           |
| **STT**              | faster-whisper (base model)  | openai-whisper, whisper.cpp, Moonshine     |
| **Intent Extraction**| DistilBERT (HF transformers) | MiniLM, RoBERTa, DeBERTa                  |
| **Response Gen**     | GPT-2 (HF) / Ollama         | Phi-4-mini, Qwen3, Gemma-4                |
| **TTS**              | Kokoro-82M                   | Coqui XTTS (legacy), Piper, Fish Speech   |
| **Audio I/O**        | librosa                      | soundfile + numpy, PyAudio                 |

#### Key Metrics / Parameters
- **Target GPU**: Kaggle T4 (16GB VRAM) / P100 (16GB VRAM)
- **faster-whisper base**: ~74M params, WER ~7-10% (English), GPU: near real-time
- **DistilBERT**: 66M params, 97% of BERT performance, 60% faster inference
- **GPT-2**: 124M params (small), autoregressive text generation
- **Kokoro-82M**: 82M params, 24kHz output, Apache 2.0 license

---

## Phase 1 — Project Setup & Scaffolding

### Operation
Created complete project directory structure, dependency manifest, central config, Gradio UI shell with stub pipeline, and seed intent dataset.

### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | NEW | All pip dependencies |
| `config.py` | NEW | Central config (models, hyperparams, device) |
| `app.py` | NEW | Gradio UI shell with full layout + stub pipeline |
| `modules/__init__.py` | NEW | Package init |
| `modules/stt.py` | NEW | SpeechToText class stub |
| `modules/intent.py` | NEW | IntentClassifier class stub |
| `modules/response.py` | NEW | ResponseGenerator class stub |
| `modules/tts.py` | NEW | TextToSpeech class stub |
| `data/intents.json` | NEW | 9-class intent dataset seed (72 examples) |

### Technical Details
- **Gradio Blocks UI**: Two-column layout — mic input (left), four outputs (right: transcript, intent, response, audio)
- **Config**: Auto-detects CUDA; all model names and generation params in one place
- **Architecture**: Each module is a class with a single public method — clean interface for pipeline wiring

---

## Phase 2 — STT Module (faster-whisper)

### Operation
Implemented the `SpeechToText` class using `faster-whisper` with `librosa` audio preprocessing. Wired it into the Gradio pipeline — microphone audio now gets transcribed live.

### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `modules/stt.py` | MODIFIED | Full implementation: model loading, audio preprocessing, VAD, transcription |
| `app.py` | MODIFIED | Activated `SpeechToText()` init + wired `stt.transcribe()` into pipeline |

### Technical Details
- **Model**: `faster-whisper` base (74M params) with CTranslate2 backend
- **Compute**: `float16` on CUDA, `int8` on CPU — auto-selected via `config.py`
- **Audio Preprocessing**: `librosa.load(path, sr=16000, mono=True)` — handles any format + resampling
- **VAD Filter**: Enabled with 500ms min silence — filters non-speech segments before decoding
- **Edge Cases**: Rejects audio < 0.5s duration, detects silence (RMS < 1e-4), catches all exceptions
- **Beam Search**: `beam_size=5` for accuracy (configurable in `config.py`)

---

## Phase 3 — Intent Extraction (DistilBERT)

### Operation
Implemented the `IntentClassifier` class using Hugging Face's `transformers` pipeline. Changed the underlying model to an MNLI fine-tuned DistilBERT to allow for zero-shot intent classification against our dynamic intent list, without requiring an explicit training step.

### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `config.py` | MODIFIED | Changed `INTENT_MODEL_NAME` to `typeform/distilbert-base-uncased-mnli` |
| `modules/intent.py` | MODIFIED | Full implementation: zero-shot classification pipeline |
| `app.py` | MODIFIED | Activated `IntentClassifier()` init + wired `intent_clf.predict()` into pipeline |

### Technical Details
- **Model**: `typeform/distilbert-base-uncased-mnli`
- **Methodology**: Zero-shot classification. The model treats intent classification as a Natural Language Inference (NLI) problem, testing if a transcribed premise entails the hypothesis "This example is about {intent}".
- **Flexibility**: Intent labels can be easily modified in `config.py` without needing to re-train the model.

---

## Phase 4 — Response Generation (GPT-2)

### Operation
Implemented the `ResponseGenerator` class using Hugging Face's `transformers` pipeline for `text-generation`. The generator takes the STT transcript and the detected intent, formats it into a simple prompt, and uses GPT-2 to autoregressively generate a conversational response.

### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `modules/response.py` | MODIFIED | Full implementation: text-generation pipeline using GPT-2 |
| `app.py` | MODIFIED | Activated `ResponseGenerator()` init + wired `response_gen.generate()` into pipeline |

### Technical Details
- **Model**: `gpt2` (124M parameters)
- **Decoding Strategy**: Uses Top-p (nucleus) sampling with `temperature=0.7` and `top_p=0.9` to provide varied but coherent responses, plus a repetition penalty to prevent looping.
- **Prompt Engineering**: Uses a basic dialogue format `"The user said: {text}\nThe intent is: {intent}\nAI Response:"` to guide the model.
- **Post-processing**: Truncates the output at the first newline to prevent the model from hallucinating a continuing conversation.

---

## Phase 5 — Text-to-Speech (Kokoro)

### Operation
Implemented the `TextToSpeech` class using the `kokoro` library. Integrated it into the pipeline so that the text generated by GPT-2 is synthesized into speech and output through the Gradio UI. The end-to-end pipeline is now fully functional.

### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `modules/tts.py` | MODIFIED | Full implementation: KPipeline initialization and synthesis |
| `app.py` | MODIFIED | Activated `TextToSpeech()` init + wired `tts_engine.synthesize()` into pipeline |

### Technical Details
- **Model**: `Kokoro-82M`
- **Output Format**: 24kHz numpy array, natively supported by Gradio's `gr.Audio(type="numpy")`.
- **Handling Multi-Sentence**: Kokoro `KPipeline` generates chunks of audio. The module iterates through the generator and concatenates these chunks into a single seamless audio array.
- **Dependencies**: Requires `espeak-ng` system dependency for Grapheme-to-Phoneme conversion.

---

## Phase 6 — Pipeline Integration & Error Handling

### Operation
Refactored the main `voice_assistant_pipeline` in `app.py` to ensure robust data validation between modules.

### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `app.py` | MODIFIED | Added early-exit returns for STT failures |

### Technical Details
- **Fail-Fast Mechanism**: If the STT module returns an empty string or an error flag (e.g., `[STT Error]`), the pipeline halts immediately and returns a warning to the UI rather than passing garbage data to DistilBERT and GPT-2.
- **Graceful Fallbacks**: The Intent extraction uses `.get()` to safely default to `"general_query"` if the dictionary format fails.

---

## Phase 7 — Gradio UI Polish

### Operation
Refactored the front-end layout in `app.py` to be more user-friendly, responsive, and aesthetically pleasing.

### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `app.py` | MODIFIED | Refactored UI layout, added Accordions and Clear Button |

### Technical Details
- **Autoplay**: Enabled `autoplay=True` on the `gr.Audio` output so the Assistant speaks immediately without the user having to click play.
- **De-cluttering**: Moved technical metadata (Intent and Confidence) into a collapsible `gr.Accordion` to keep the UI focused on the conversation.
- **HTML Headers**: Replaced markdown text with styled HTML components for a more professional look.
- **Clear Button**: Added `gr.ClearButton` hooked into all I/O components so the user can easily reset the app state.

---

## 🚀 MAJOR PIVOT: Customer Support Agent

The project was pivoted from a general zero-shot assistant to a specialized **E-Commerce Customer Support Agent**. This involved generating synthetic data and explicitly fine-tuning the models.

### Pivot Phase 1 — Intent Fine-Tuning (DistilBERT)

#### Operation
Replaced the slow, generic `zero-shot-classification` pipeline with a fast, supervised `text-classification` model explicitly fine-tuned on e-commerce support intents.

#### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `data/support_intents.json` | NEW | Synthetic dataset mapping e-commerce queries to 5 core intents |
| `scripts/train_intent.py` | NEW | Hugging Face `Trainer` script to fine-tune DistilBERT on GPU |
| `config.py` | MODIFIED | Pointed `INTENT_MODEL_NAME` to the local fine-tuned weights |
| `modules/intent.py` | MODIFIED | Refactored pipeline to `text-classification` |

#### Technical Details
- **Intents**: `track_order`, `refund_request`, `speak_to_human`, `product_info`, `cancel_order`.
- **Training**: Fine-tuned `distilbert-base-uncased` over 5 epochs using the `datasets` and `transformers` libraries on a Kaggle T4 GPU.
- **Performance**: The custom sequence classification head evaluates user input instantly, without the overhead of computing NLI entailment pairs.

---

### Pivot Phase 2 — Response Fine-Tuning (GPT-2)

#### Operation
Fine-tuned GPT-2 (124M) on 50 synthetic customer support dialogues to replace generic text generation with professional, domain-specific agent responses. Created training data, wrote the fine-tuning script, refactored the prompt format, and updated config to load fine-tuned weights.

#### Files Changed
| File | Action | Purpose |
|------|--------|---------|
| `data/support_dialogues.json` | NEW | 50 synthetic customer support dialogues (10 per intent) with professional agent responses |
| `scripts/train_response.py` | NEW | GPT-2 Causal LM fine-tuning script using HuggingFace Trainer with DataCollatorForLanguageModeling |
| `modules/response.py` | MODIFIED | Changed prompt format to `### Intent: {intent}\n### Customer: {text}\n### Agent:` + stop-marker truncation |
| `config.py` | MODIFIED | Changed `RESPONSE_MODEL_NAME` from `"gpt2"` to `"models/response_finetuned"` |

#### Technical Details
- **Prompt Template**: `### Intent: {intent}\n### Customer: {text}\n### Agent:` — this format must be identical between training data and inference to ensure the model generates coherent responses.
- **Training Objective**: Causal Language Modeling (CLM) — the model learns to predict the next token given all previous tokens, trained end-to-end on the full dialogue sequence.
- **Data Collation**: Uses `DataCollatorForLanguageModeling(mlm=False)` from HuggingFace — handles dynamic padding and creates `labels` identical to `input_ids` (shifted internally by the model) for the causal LM loss.
- **Stop-Marker Truncation**: Post-generation, the output is truncated at stop markers (`### Customer:`, `### Intent:`, `###`) to prevent the model from hallucinating additional conversation turns.
- **Dataset**: 50 dialogue examples across 5 intents (10 per intent: `track_order`, `refund_request`, `speak_to_human`, `product_info`, `cancel_order`).
