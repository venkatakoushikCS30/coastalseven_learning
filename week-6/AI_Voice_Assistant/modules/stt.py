"""
STT Module — Speech-to-Text using faster-whisper.
Converts audio file/array → transcribed text.

Uses CTranslate2 backend for 3-4× speedup over vanilla Whisper.
Supports GPU (float16) and CPU (int8) inference.
"""

import librosa
import numpy as np
from faster_whisper import WhisperModel

import config


class SpeechToText:
    """
    Wraps faster-whisper for speech-to-text transcription.

    Usage:
        stt = SpeechToText()            # loads model once
        text = stt.transcribe("audio.wav")
    """

    def __init__(self):
        print(f"[STT] Loading Whisper '{config.STT_MODEL_SIZE}' "
              f"(compute={config.STT_COMPUTE_TYPE}, device={config.DEVICE})...")

        self.model = WhisperModel(
            config.STT_MODEL_SIZE,
            device=config.DEVICE,
            compute_type=config.STT_COMPUTE_TYPE,
        )
        print("[STT] Model loaded ✓")

    def _preprocess_audio(self, audio_path: str) -> np.ndarray:
        """
        Load audio from any format and resample to 16kHz mono.

        Args:
            audio_path: Path to the audio file (wav, mp3, ogg, etc.)

        Returns:
            np.ndarray of float32 audio samples at 16kHz
        """
        # librosa.load handles resampling + mono conversion in one call
        audio, sr = librosa.load(audio_path, sr=config.AUDIO_SAMPLE_RATE, mono=True)
        return audio

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file → text string.

        Args:
            audio_path: Path to audio file (from Gradio's gr.Audio filepath output)

        Returns:
            Transcribed text string. Returns empty string on failure.
        """
        try:
            # Preprocess: load + resample to 16kHz mono
            audio = self._preprocess_audio(audio_path)

            # Validate: skip if audio is too short (< 0.5s) or silent
            duration = len(audio) / config.AUDIO_SAMPLE_RATE
            if duration < 0.5:
                return "[STT] Audio too short (< 0.5s)"

            rms = np.sqrt(np.mean(audio ** 2))
            if rms < 1e-4:
                return "[STT] Audio is silent"

            # Transcribe with faster-whisper
            segments, info = self.model.transcribe(
                audio,
                beam_size=config.STT_BEAM_SIZE,
                language=config.STT_LANGUAGE,
                vad_filter=True,           # filter out non-speech segments
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                ),
            )

            # Collect all segment texts
            transcript = " ".join(seg.text.strip() for seg in segments)
            transcript = transcript.strip()

            if not transcript:
                return "[STT] No speech detected"

            print(f"[STT] Transcribed ({info.language}, "
                  f"prob={info.language_probability:.2f}, "
                  f"dur={info.duration:.1f}s): {transcript[:80]}...")

            return transcript

        except Exception as e:
            print(f"[STT] Error: {e}")
            return f"[STT Error] {str(e)}"
