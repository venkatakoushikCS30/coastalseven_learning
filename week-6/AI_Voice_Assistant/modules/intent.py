"""
Intent Module — Intent extraction using fine-tuned DistilBERT.
Classifies transcribed text → one of 5 customer support intent labels.

Uses a supervised text-classification pipeline with a DistilBERT model
fine-tuned on synthetic e-commerce support data (data/support_intents.json).
"""

from transformers import pipeline
import config

class IntentClassifier:
    """
    Classifies transcribed text into one of the predefined customer support intents.
    """

    def __init__(self):
        print(f"[Intent] Loading Fine-Tuned DistilBERT from '{config.INTENT_MODEL_NAME}' "
              f"on {config.DEVICE}...")
        
        device_id = 0 if config.DEVICE == "cuda" else -1
        
        # We now use the standard 'text-classification' pipeline
        # which is MUCH faster than the old zero-shot pipeline!
        self.classifier = pipeline(
            "text-classification",
            model=config.INTENT_MODEL_NAME,
            tokenizer=config.INTENT_MODEL_NAME,
            device=device_id
        )
        print("[Intent] Model loaded ✓")

    def predict(self, text: str) -> dict:
        """
        Predict the intent of the given text.
        
        Returns:
            Dictionary with 'intent' (str) and 'confidence' (float)
        """
        if not text.strip():
            return {"intent": "unknown", "confidence": 0.0}

        try:
            # The pipeline returns a list of dicts: [{'label': 'track_order', 'score': 0.99}]
            result = self.classifier(text, truncation=True, max_length=config.INTENT_MAX_LENGTH)[0]
            
            intent_label = result["label"]
            confidence = result["score"]
            
            print(f"[Intent] Detected: '{intent_label}' (conf: {confidence:.2f})")
            return {"intent": intent_label, "confidence": confidence}
            
        except Exception as e:
            print(f"[Intent] Error during classification: {e}")
            return {"intent": "general_query", "confidence": 0.0}
