import gradio as gr
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

model_id = "Salesforce/blip2-opt-2.7b"
print(f"Loading {model_id} on {device}... (This might take a moment depending on your internet speed)")

processor = Blip2Processor.from_pretrained(model_id)

model = Blip2ForConditionalGeneration.from_pretrained(
    model_id, 
    torch_dtype=dtype,
    device_map="auto" if device == "cuda" else None
)

if device == "cpu":
    model.to(device)

def generate_caption(image):
    if image is None:
        return "Please upload an image to get started."
    
    inputs = processor(images=image, return_tensors="pt").to(device, dtype)
    
    generated_ids = model.generate(**inputs, max_new_tokens=50)
    
    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    
    return caption

demo = gr.Interface(
    fn=generate_caption,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=gr.Textbox(label="BLIP-2 Caption", lines=2),
    title="BLIP-2 Image Caption Generator",
    description="Upload any image, and the BLIP-2 model will analyze it and generate a descriptive caption.",
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch()