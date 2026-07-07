"""
Central configuration for the AI Voice Assistant.
All model names, paths, and hyperparameters live here.
"""

import torch

# ── Device ──────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ── STT (faster-whisper) ────────────────────────────────
STT_MODEL_SIZE = "base"            # tiny | base | small | medium | large-v3
STT_COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"
STT_BEAM_SIZE = 5
STT_LANGUAGE = "en"

# ── Intent Extraction (DistilBERT) ─────────────────────
INTENT_MODEL_NAME = "models/intent_finetuned"  # Local fine-tuned model
INTENT_LABELS = [
    "cancel_order",
    "product_info",
    "refund_request",
    "speak_to_human",
    "track_order"
]
INTENT_MAX_LENGTH = 128            # max token length for classifier input

# ── Response Generation (GPT-2) ────────────────────────
RESPONSE_MODEL_NAME = "models/response_finetuned"  # Local fine-tuned model
RESPONSE_MAX_NEW_TOKENS = 150
RESPONSE_TEMPERATURE = 0.7
RESPONSE_TOP_P = 0.9
RESPONSE_REPETITION_PENALTY = 1.2

# ── TTS (Kokoro) ───────────────────────────────────────
TTS_LANG_CODE = "a"                # 'a' = American English
TTS_VOICE = "af_heart"             # default voice preset
TTS_SAMPLE_RATE = 24000

# ── Audio I/O ──────────────────────────────────────────
AUDIO_SAMPLE_RATE = 16000          # Whisper expects 16kHz mono
