import os
import sys
import gradio as gr

from src.chatbot import FAQChatbot
from src.predictor import IntentPredictor

def build_app():
    # Load predictor and chatbot
    print("Loading models and initializing FAQ Chatbot...", file=sys.stderr)
    try:
        predictor = IntentPredictor()
        chatbot = FAQChatbot(predictor=predictor)
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Application initialized. Launching Gradio interface...", file=sys.stderr)

    # Custom CSS for modern styling
    custom_css = """
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
    
    .gradio-container {
        font-family: 'Inter', sans-serif !important;
        max-width: 1100px !important;
        margin: auto !important;
    }
    
    .title-header h1 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    
    .title-header p {
        font-family: 'Inter', sans-serif !important;
        color: #4B5563;
        font-size: 1.1rem;
    }
    
    .chat-column {
        background: white !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    }

    .analysis-column {
        background: #F9FAFB !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02) !important;
    }
    """

    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"), css=custom_css) as demo:
        # Header block
        gr.HTML(
            """
            <div class="title-header" style="text-align: center; margin-bottom: 25px; margin-top: 15px;">
                <h1 style="font-size: 2.6rem; margin-bottom: 8px;">FAQ Intent Classification Chatbot</h1>
                <p>An intelligent customer-support system powered by a fine-tuned DistilBERT classifier (14 Intents)</p>
            </div>
            """
        )
        
        with gr.Row():
            # Left Column - Chat
            with gr.Column(scale=3, elem_classes="chat-column"):
                chatbot_ui = gr.Chatbot(
                    label="Customer Support Console", 
                    height=500,
                    show_label=True
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="",
                        placeholder="Type your question here (e.g. Can I return my order?)...",
                        show_label=False,
                        scale=8,
                        container=False
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat History", variant="stop")

            # Right Column - Analysis
            with gr.Column(scale=2, elem_classes="analysis-column"):
                gr.Markdown("### 🔍 Real-Time NLP Diagnostics")
                gr.Markdown("Submit a message in the chat to see real-time classification metrics.")
                
                intent_badge = gr.Textbox(
                    label="Predicted Intent Class", 
                    value="None", 
                    interactive=False
                )
                
                confidence_meter = gr.Slider(
                    label="Confidence Score", 
                    minimum=0.0, 
                    maximum=1.0, 
                    value=0.0, 
                    interactive=False
                )
                
                prob_label = gr.Label(
                    label="Top 5 Intent Probabilities", 
                    num_top_classes=5
                )

        # Message processing logic
        def process_user_input(message, chat_history):
            if not message.strip():
                return chat_history, "", "None", 0.0, {}
            
            # Get response from chatbot
            res = chatbot.process_message(message)
            response = res["response"]
            intent = res["intent"]
            confidence = res["confidence"]
            
            # Format top 5 probabilities
            top_5 = dict(list(res["probabilities"].items())[:5])
            
            # Detect history format dynamically
            is_dict_format = False
            if chat_history:
                if isinstance(chat_history[0], dict):
                    is_dict_format = True
            else:
                # Default to dict format for newer Gradio (v5/v6)
                is_dict_format = True
                
            if is_dict_format:
                new_history = list(chat_history or []) + [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response}
                ]
            else:
                new_history = list(chat_history or []) + [[message, response]]
            
            return new_history, "", intent, confidence, top_5

        # Chat clear logic
        def clear_chat():
            chatbot.clear_history()
            return [], "", "None", 0.0, {}

        # Connect event handlers
        msg_input.submit(
            fn=process_user_input, 
            inputs=[msg_input, chatbot_ui], 
            outputs=[chatbot_ui, msg_input, intent_badge, confidence_meter, prob_label]
        )
        
        send_btn.click(
            fn=process_user_input, 
            inputs=[msg_input, chatbot_ui], 
            outputs=[chatbot_ui, msg_input, intent_badge, confidence_meter, prob_label]
        )
        
        clear_btn.click(
            fn=clear_chat, 
            inputs=None, 
            outputs=[chatbot_ui, msg_input, intent_badge, confidence_meter, prob_label]
        )
        
        # Example queries
        gr.Examples(
            examples=[
                "How do I track my order?",
                "Can I cancel my monthly subscription?",
                "My credit card was declined at checkout.",
                "I want to permanently delete my account.",
                "What is your return policy?"
            ],
            inputs=msg_input,
            label="Try these sample queries:"
        )

    return demo

if __name__ == "__main__":
    demo = build_app()
    # Launch local server
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
