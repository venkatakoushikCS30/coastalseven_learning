import sys
from pathlib import Path

# Add src to python path so we can import modules easily
PROJ_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJ_ROOT / "src"))

import streamlit as st
import torch
import yaml
import json
from PIL import Image

from model import build_model
from augmentations import get_val_transforms
from inference import predict_image

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Plant Disease Detector",
    page_icon="🌿",
    layout="wide"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2e7d32;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-box {
        background-color: #f1f8e9;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 2px solid #c5e1a5;
    }
    .disease-name {
        font-size: 1.8rem;
        font-weight: bold;
        color: #d32f2f;
    }
    .healthy-name {
        font-size: 1.8rem;
        font-weight: bold;
        color: #388e3c;
    }
    .confidence {
        font-size: 1.2rem;
        color: #616161;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- CACHING & SETUP ---
@st.cache_resource
def load_app_resources():
    try:
        # Load config
        with open(PROJ_ROOT / "configs" / "hw_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Load class names
        with open(PROJ_ROOT / "configs" / "class_names.json", "r", encoding="utf-8") as f:
            class_names = json.load(f)
            
        device = torch.device(config["hyperparameters"]["device"])
        
        # Load model
        model = build_model(num_classes=len(class_names), pretrained=False)
        checkpoint_path = PROJ_ROOT / "models" / "best_finetune.pth"
        
        if not checkpoint_path.exists():
            return None, None, None, None, "Checkpoint not found! Train the model first."
            
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        model.eval()
        
        # Transform
        image_size = config["hyperparameters"]["image_size"]
        transform = get_val_transforms(image_size)
        
        return model, transform, class_names, device, None
        
    except Exception as e:
        return None, None, None, None, f"Error loading resources: {str(e)}"

# Load everything once
model, transform, class_names, device, error_msg = load_app_resources()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=100)
    st.header("About")
    st.info("""
    This application uses a deep learning model (ResNet18) trained on the **PlantVillage** dataset.
    
    It classifies images of crop leaves into healthy or diseased categories.
    """)
    if class_names:
        st.write(f"**Supported Classes:** {len(class_names)}")
        with st.expander("View All Classes"):
            for c in class_names:
                st.write(f"- {c}")

# --- MAIN UI ---
st.markdown('<p class="main-header">🌿 Plant Disease Detector</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload a picture of a leaf to instantly identify potential diseases.</p>', unsafe_allow_html=True)

if error_msg:
    st.error(error_msg)
    st.stop()

# File Uploader
uploaded_file = st.file_uploader("Choose a leaf image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Two columns for layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("Uploaded Image")
        # Read image
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
    with col2:
        st.subheader("Analysis Results")
        with st.spinner("Analyzing leaf..."):
            # Predict
            pred_class, conf = predict_image(image, model, transform, class_names, device)
            
            # Formatting class name nicely
            nice_name = pred_class.replace("_", " ").replace("  ", " ").strip()
            
            is_healthy = "healthy" in nice_name.lower()
            css_class = "healthy-name" if is_healthy else "disease-name"
            icon = "✅" if is_healthy else "⚠️"
            
            st.markdown(f"""
            <div class="prediction-box">
                <p style="font-size: 1.2rem; margin-bottom: 5px;">Detected Condition:</p>
                <p class="{css_class}">{icon} {nice_name}</p>
                <p class="confidence">Confidence: <b>{conf*100:.2f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar for confidence
            st.progress(conf)
            
            if not is_healthy:
                st.warning("A disease has been detected. Please consult agricultural guidelines or an expert for treatment options.")
            else:
                st.success("The leaf appears to be healthy!")
