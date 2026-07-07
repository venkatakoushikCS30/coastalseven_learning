"""
AI Voice Assistant — Customer Support Agent
Pipeline: Microphone → Whisper STT → DistilBERT Intent → GPT-2 Response → Kokoro TTS → Playback
All models are fine-tuned on e-commerce customer support data.
"""

import gradio as gr
import numpy as np
import config

# ── Module Imports ──────────────────────────────────────
from modules.stt import SpeechToText
from modules.intent import IntentClassifier
from modules.response import ResponseGenerator
from modules.tts import TextToSpeech


# ── Initialize Pipeline Components ──────────────────────
print(f"[INFO] Device: {config.DEVICE}")
stt = SpeechToText()
intent_clf = IntentClassifier()       # Fine-tuned DistilBERT
response_gen = ResponseGenerator()    # Fine-tuned GPT-2
tts_engine = TextToSpeech()           # Kokoro-82M


# ── Pipeline Function ───────────────────────────────────
def voice_assistant_pipeline(audio):
    """
    End-to-end pipeline:
    audio (filepath) → transcript → intent → response text → speech audio
    """
    if audio is None:
        return "⚠️ No audio received.", "", "", None

    # Step 1: STT — transcribe audio to text
    transcript = stt.transcribe(audio)
    if not transcript or transcript.startswith("[STT"):
        # If STT failed or returned an error message, halt pipeline
        return transcript if transcript else "⚠️ Could not transcribe audio.", "", "", None

    # Step 2: Intent — classify the transcript
    result = intent_clf.predict(transcript)
    intent = result.get("intent", "general_query")
    confidence = result.get("confidence", 0.0)

    # Step 3: Response — generate reply
    response_text = response_gen.generate(transcript, intent)

    # Step 4: TTS — synthesize speech
    sr, audio_out = tts_engine.synthesize(response_text)
    
    # Format for Gradio output: (sample_rate, numpy_array)
    if audio_out is not None:
        final_audio = (sr, audio_out)
    else:
        final_audio = None

    return transcript, f"{intent} ({confidence:.2f})", response_text, final_audio


# ── Gradio UI ───────────────────────────────────────────
with gr.Blocks(
    title="🎙️ AI Voice Assistant",
    theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="blue"),
) as demo:

    gr.Markdown(
        """
        <div style='text-align: center;'>
            <h1>🎙️ AI Customer Support Agent</h1>
            <h3>E-Commerce Voice Assistant — Powered by Fine-Tuned Models</h3>
            <p><strong>Pipeline:</strong> Whisper STT → DistilBERT Intent → GPT-2 Response → Kokoro TTS</p>
        </div>
        """
    )

    with gr.Row():
        # ── Left Column: Input ──
        with gr.Column(scale=1):
            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="filepath",
                label="🎤 Speak or Upload Audio",
            )
            submit_btn = gr.Button("🚀 Process", variant="primary", size="lg")

        # ── Right Column: Outputs ──
        with gr.Column(scale=2):
            audio_output = gr.Audio(label="🔊 Spoken Response (TTS)", type="numpy", autoplay=True)
            
            with gr.Group():
                transcript_out = gr.Textbox(label="📝 You Said", lines=2, placeholder="Waiting for audio...")
                response_out = gr.Textbox(label="💬 AI Replied", lines=3, placeholder="Generating response...")
                
            # Technical details hidden in an accordion for cleaner UI
            with gr.Accordion("⚙️ Technical Details (Intent & Confidence)", open=False):
                intent_out = gr.Textbox(label="🎯 Detected Intent", lines=1)

    with gr.Row():
        clear_btn = gr.ClearButton([audio_input, transcript_out, intent_out, response_out, audio_output], value="🗑️ Clear All")

    # ── Wire the pipeline ──
    submit_btn.click(
        fn=voice_assistant_pipeline,
        inputs=[audio_input],
        outputs=[transcript_out, intent_out, response_out, audio_output],
    )

    gr.Markdown(
        """
        ---
        *All models fine-tuned on e-commerce customer support data. Built with faster-whisper, DistilBERT, GPT-2, and Kokoro.*
        """
    )

# ── Launch ──────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(debug=True, share=True)
