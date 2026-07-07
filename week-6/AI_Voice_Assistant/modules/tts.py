"""
TTS Module — Text-to-Speech using Kokoro-82M.
Converts response text → audio waveform.

Uses Kokoro, a highly efficient 82M parameter TTS model.
"""

import numpy as np
from kokoro import KPipeline
import config

class TextToSpeech:
    """
    Kokoro Text-to-Speech synthesizer.
    
    Usage:
        tts = TextToSpeech()
        sr, audio = tts.synthesize("Hello world")
    """

    def __init__(self):
        print(f"[TTS] Loading Kokoro Pipeline (lang='{config.TTS_LANG_CODE}') "
              f"on {config.DEVICE}...")
        
        # Initialize the pipeline
        # Kokoro automatically handles device mapping under the hood
        # but requires 'espeak-ng' installed on the system.
        self.pipeline = KPipeline(lang_code=config.TTS_LANG_CODE)
        self.voice = config.TTS_VOICE
        self.sample_rate = config.TTS_SAMPLE_RATE
        
        print("[TTS] Model loaded ✓")

    def synthesize(self, text: str) -> tuple:
        """
        Convert text to audio.
        
        Args:
            text: The response string to synthesize.
            
        Returns:
            Tuple of (sample_rate: int, audio_data: np.ndarray)
            Returns (None, None) on failure.
        """
        if not text:
            print("[TTS] Empty text provided, skipping synthesis.")
            return None, None
            
        print(f"[TTS] Synthesizing audio for: '{text[:50]}...'")
        
        try:
            # The pipeline returns a generator. 
            # We iterate through it and concatenate the audio chunks.
            generator = self.pipeline(
                text, 
                voice=self.voice,
                speed=1.0,
                split_pattern=r'\n+' # Split on newlines if multiple sentences exist
            )
            
            audio_chunks = []
            for i, (graphemes, phonemes, audio) in enumerate(generator):
                audio_chunks.append(audio)
                
            if not audio_chunks:
                print("[TTS] Pipeline generated no audio chunks.")
                return None, None
                
            # Concatenate all generated audio chunks into a single numpy array
            combined_audio = np.concatenate(audio_chunks)
            
            print(f"[TTS] Synthesis complete. Audio shape: {combined_audio.shape}")
            
            # Gradio Audio component expects (sample_rate, numpy_array)
            return self.sample_rate, combined_audio
            
        except Exception as e:
            print(f"[TTS] Error during synthesis: {e}")
            return None, None
