import sys
from typing import Dict, Any, List

from src.predictor import IntentPredictor

class FAQChatbot:
    def __init__(self, predictor: IntentPredictor = None, confidence_threshold: float = 0.30):
        """Initialize the chatbot wrapper with memory, templates, and predictor."""
        self.predictor = predictor or IntentPredictor()
        self.confidence_threshold = confidence_threshold
        self.history: List[Dict[str, Any]] = []
        self.pending_action: str = None  # To track state machine context (e.g., 'account_delete')

        # Intent responses dictionary
        self.responses = {
            "account_delete": (
                "I can help you delete your account. However, please note that this action is permanent. "
                "You will lose all your order history, saved addresses, and active rewards. "
                "Are you sure you want to proceed? Please type 'Yes' to confirm or 'No' to cancel."
            ),
            "account_login": (
                "To log in to your account, click the 'Sign In' button at the top right of our website. "
                "You can use your email and password, or authenticate using your Google or Apple account."
            ),
            "billing_payment": (
                "We accept Visa, MasterCard, American Express, PayPal, Apple Pay, and Google Pay. "
                "You can manage your payment methods under 'Billing & Payments' in your Account Settings."
            ),
            "contact_support": (
                "You can reach our customer support team via email at support@example.com, "
                "or call us toll-free at 1-800-555-0199 (Monday to Friday, 9:00 AM - 6:00 PM EST)."
            ),
            "feature_request": (
                "We appreciate your ideas! Please describe the feature you'd like to see. "
                "I will log this feedback and share it with our product development team."
            ),
            "hours_location": (
                "Our retail store is located at 123 Main Street, Suite 100, New York, NY. "
                "We are open Monday through Saturday from 9:00 AM to 8:00 PM, and Sunday from 10:00 AM to 6:00 PM."
            ),
            "password_reset": (
                "To reset your password, click the 'Forgot Password' link on the sign-in page. "
                "Enter your registered email address, and we will email you a secure link to set a new password."
            ),
            "product_info": (
                "Detailed specifications, dimensions, materials, and user guides can be found directly "
                "on each product's page under the 'Description' and 'Specifications' tabs."
            ),
            "refund_request": (
                "Refunds are processed to the original payment method within 5-7 business days of approval. "
                "To initiate a refund, please go to 'My Orders', click on the purchase, and select 'Request Refund'."
            ),
            "return_exchange": (
                "We offer a 30-day window for returns and exchanges on unused items in their original packaging. "
                "Use our online Returns Portal to download a prepaid shipping label."
            ),
            "shipping_status": (
                "Standard shipping takes 3-5 business days. Once your order ships, you will receive an email "
                "with a tracking link. You can also view active shipments under 'Order Tracking' in your profile."
            ),
            "subscription_cancel": (
                "You can cancel your subscription at any time. Go to 'My Subscriptions' in your profile "
                "and select 'Cancel Subscription'. Your access will remain active until the end of the current billing cycle."
            ),
            "technical_support": (
                "If you are experiencing issues with our website or app, try clearing your browser's "
                "cache and cookies. If the issue continues, please email details and screenshots to tech-support@example.com."
            ),
            "warranty_claim": (
                "Our products are backed by a 1-year limited warranty. To submit a claim, please gather your "
                "proof of purchase and photos of the defect, then complete the form on our Warranty page."
            )
        }

    def process_message(self, user_text: str) -> Dict[str, Any]:
        """Process user input, apply state checks, run classifier, and return response."""
        user_text_clean = user_text.strip()
        if not user_text_clean:
            return {
                "response": "I didn't hear anything. How can I help you?",
                "intent": "none",
                "confidence": 0.0,
                "history": self.history
            }

        # 1. State check: Context-based confirmation handling
        if self.pending_action:
            action = self.pending_action
            user_lower = user_text_clean.lower()
            
            # Simple confirmation matching
            is_yes = user_lower in ["yes", "y", "yep", "sure", "confirm", "yeah", "please"]
            is_no = user_lower in ["no", "n", "nope", "cancel", "stop", "don't"]

            if is_yes:
                if action == "account_delete":
                    response = (
                        "Understood. Your request for permanent account deletion has been registered. "
                        "We will process this within 24 hours. A confirmation email has been sent to your inbox. "
                        "Is there anything else I can help you with?"
                    )
                else:
                    response = f"Action '{action}' has been confirmed and processed."
                
                self.pending_action = None
                intent = "confirmation_yes"
                confidence = 1.0
            elif is_no:
                response = f"Understood. The action has been cancelled. Your account settings remain unchanged."
                self.pending_action = None
                intent = "confirmation_no"
                confidence = 1.0
            else:
                response = (
                    "I'm sorry, I need a clear confirmation. "
                    "Do you want to proceed? Please type 'Yes' to confirm or 'No' to cancel."
                )
                intent = "confirmation_invalid"
                confidence = 0.0
                
            # Log to history
            self.history.append({"role": "user", "text": user_text_clean, "intent": intent, "confidence": confidence})
            self.history.append({"role": "assistant", "text": response, "intent": intent, "confidence": confidence})
            
            return {
                "response": response,
                "intent": intent,
                "confidence": confidence,
                "history": self.history,
                "probabilities": {intent: confidence}
            }

        # 2. Predict intent
        try:
            pred_res = self.predictor.predict(user_text_clean)
            intent = pred_res["intent"]
            confidence = pred_res["confidence"]
        except Exception as e:
            # Fallback for classification error
            intent = "error"
            confidence = 0.0
            pred_res = {"probabilities": {}}

        # 3. Formulate response
        if confidence < self.confidence_threshold:
            # Under confidence threshold
            response = (
                "I'm not quite sure how to help with that. Could you please rephrase your request? "
                "For further assistance, you can also ask to speak with human support."
            )
            logged_intent = "low_confidence_fallback"
        else:
            # Match response template
            response = self.responses.get(intent, "I'm sorry, I don't have information on that topic.")
            logged_intent = intent
            
            # Trigger state machine for confirmation if needed
            if intent == "account_delete":
                self.pending_action = "account_delete"

        # 4. Save history
        self.history.append({"role": "user", "text": user_text_clean, "intent": logged_intent, "confidence": confidence})
        self.history.append({"role": "assistant", "text": response, "intent": logged_intent, "confidence": confidence})

        return {
            "response": response,
            "intent": logged_intent,
            "confidence": confidence,
            "history": self.history,
            "probabilities": pred_res.get("probabilities", {})
        }

    def clear_history(self):
        """Clear chatbot memory and pending states."""
        self.history.clear()
        self.pending_action = None

if __name__ == "__main__":
    print("Initializing FAQ Chatbot wrapper...", file=sys.stderr)
    try:
        chatbot = FAQChatbot()
        print("\nChatbot initialized! Type 'exit', 'quit', or 'clear' to interact.", file=sys.stderr)
        print("=" * 60)
        print("Bot: Hello! I am your FAQ support assistant. How can I help you today?")
        
        while True:
            try:
                user_msg = input("You: ")
                if user_msg.strip().lower() in ["exit", "quit"]:
                    print("Bot: Goodbye!")
                    break
                elif user_msg.strip().lower() == "clear":
                    chatbot.clear_history()
                    print("System: Conversation history cleared.", file=sys.stderr)
                    print("\nBot: Hello! History cleared. How can I help you today?")
                    continue
                    
                result = chatbot.process_message(user_msg)
                print(f"Bot: {result['response']}")
                
                # Debug logging in terminal
                print(f"   [Intent: {result['intent']} | Conf: {result['confidence']:.4f} | Pending: {chatbot.pending_action}]", file=sys.stderr)
            except KeyboardInterrupt:
                print("\nBot: Goodbye!")
                break
    except Exception as e:
        print(f"Failed to start chatbot: {e}", file=sys.stderr)
        sys.exit(1)
