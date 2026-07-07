"""
Response Module — Response generation using fine-tuned GPT-2.
Generates a professional customer support reply given intent + user text.

The prompt format MUST match exactly what was used during training
in scripts/train_response.py:
    ### Intent: {intent}
    ### Customer: {user}
    ### Agent: {response}
"""

from transformers import pipeline, set_seed
import config

class ResponseGenerator:
    """
    Fine-tuned GPT-2 for generating customer support responses.
    
    Usage:
        gen = ResponseGenerator()
        reply = gen.generate("Where is my package?", "track_order")
    """

    def __init__(self):
        print(f"[Response] Loading GPT-2 '{config.RESPONSE_MODEL_NAME}' "
              f"on {config.DEVICE}...")
        
        device_id = 0 if config.DEVICE == "cuda" else -1
        
        self.generator = pipeline(
            "text-generation",
            model=config.RESPONSE_MODEL_NAME,
            tokenizer=config.RESPONSE_MODEL_NAME,
            device=device_id
        )
        # GPT-2 has no pad token — use eos
        self.generator.tokenizer.pad_token = self.generator.tokenizer.eos_token
        
        set_seed(42)
        print("[Response] Model loaded ✓")

    def _build_prompt(self, text: str, intent: str) -> str:
        """
        Construct the prompt using the EXACT format used during training.
        We provide intent + customer query and let the model complete the Agent response.
        """
        prompt = f"### Intent: {intent}\n### Customer: {text}\n### Agent:"
        return prompt

    def generate(self, text: str, intent: str) -> str:
        """
        Generate a response string given user text and detected intent.
        
        Args:
            text: Transcribed user input
            intent: Detected intent string
            
        Returns:
            Generated response string
        """
        prompt = self._build_prompt(text, intent)
        
        try:
            outputs = self.generator(
                prompt,
                max_new_tokens=config.RESPONSE_MAX_NEW_TOKENS,
                temperature=config.RESPONSE_TEMPERATURE,
                top_p=config.RESPONSE_TOP_P,
                repetition_penalty=config.RESPONSE_REPETITION_PENALTY,
                do_sample=True,
                return_full_text=False,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            
            response_text = outputs[0]["generated_text"].strip()
            
            # The model may generate text beyond the agent's reply.
            # Truncate at any marker that indicates a new turn.
            for stop_marker in ["### Intent:", "### Customer:", "\n###", "\n\n"]:
                if stop_marker in response_text:
                    response_text = response_text.split(stop_marker)[0].strip()
                
            if not response_text:
                response_text = "I'm not sure how to respond to that. Let me connect you to a human agent."
                
            print(f"[Response] Generated: '{response_text}'")
            return response_text
            
        except Exception as e:
            print(f"[Response] Error during generation: {e}")
            return "Sorry, I encountered an error generating a response."
