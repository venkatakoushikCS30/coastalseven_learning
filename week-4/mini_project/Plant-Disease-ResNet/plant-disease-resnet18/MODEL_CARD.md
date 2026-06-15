# Model Card: Plant Disease Detection (ResNet18)

## 1. Model Details
- **Architecture:** ResNet18 (PyTorch)
- **Base Model:** Pre-trained on ImageNet1k
- **Task:** Multi-class Image Classification
- **Classes:** 15 distinct categories (healthy and diseased states of Tomato, Potato, and Bell Pepper leaves)
- **Input Format:** RGB Images, normalized and center-cropped to 128x128 pixels

## 2. Intended Use
- **Primary Use Case:** Identifying diseases in agricultural crops from photographs of individual leaves to aid farmers, botanists, and agricultural hobbyists.
- **Out-of-Scope Use Cases:** Diagnosis of crops not present in the training set (e.g., Apple, Corn, Grapes), or images that are not explicitly focused on a leaf.

## 3. Training Data
- **Dataset:** PlantVillage Dataset
- **Total Images:** 20,638
- **Data Splits:** 
  - Train: 70% (14,440 images)
  - Validation: 15% (3,089 images)
  - Test: 15% (3,109 images)
- **Pre-processing:** Aggressive data augmentation (Random Resized Cropping, Rotations, Horizontal/Vertical Flips, Color Jittering) was applied to the training set to simulate varied field conditions and prevent overfitting.

## 4. Evaluation Results
- **Overall Test Accuracy:** 92.0%
- **Macro F1-Score:** 0.92
- **Notable Performance:** 
  - Exceedingly high accuracy (98-99% F1-score) on Healthy variants and distinct viral infections (e.g., Tomato Yellow Leaf Curl Virus).
  - Reduced accuracy (77% F1-score) when distinguishing between visually similar fungal blights (e.g., Tomato Early Blight vs. Target Spot).

## 5. Ethical Considerations & Limitations
- **Laboratory Conditions Bias:** The PlantVillage dataset predominantly features leaves placed on controlled, homogeneous backgrounds (e.g., gray or black sheets). Real-world images in chaotic field environments with varied lighting or overlapping leaves may experience a drop in accuracy.
- **Supplementary Aid Only:** The model might occasionally classify early-stage diseases as "Healthy," which could delay treatment. Users must use this tool as a supplementary diagnostic aid rather than an absolute source of truth. Consult an agricultural expert for severe crop threats.

## 6. Deployment
- **Method:** Accessible via an interactive Streamlit Web Application (`app.py`).
- **Hardware Profile:** The model and inference pipeline have been specifically optimized to run rapidly on standard CPU architectures, eliminating the need for expensive dedicated GPUs.
