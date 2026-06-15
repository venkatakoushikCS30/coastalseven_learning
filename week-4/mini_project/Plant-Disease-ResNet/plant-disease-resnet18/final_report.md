# Plant Disease Detection: Final Project Report

## 1. Executive Summary
This project successfully delivered a robust, end-to-end deep learning pipeline for detecting plant diseases from leaf images. By employing transfer learning with a ResNet18 architecture and aggressive data augmentation, the model achieved a **92.0% accuracy** on a hold-out test set of over 3,000 images. The final deliverable includes a fully interactive Streamlit Web Application that allows users to upload images for instant, locally-hosted diagnosis.

## 2. Hardware Optimization
A critical constraint of this project was the lack of a dedicated CUDA GPU. To overcome the computational bottleneck of training a deep neural network on a standard Intel CPU, several vital optimizations were implemented:
- **Image Resizing:** Input resolution was reduced from its native size to `128x128`, drastically reducing the floating-point operations per second (FLOPS) required.
- **Multiprocessing Overheads:** PyTorch DataLoaders were strictly set to `num_workers=0` to prevent excessive multiprocessing overheads on Windows CPU environments.
- **Batch Size Tuning:** The batch size was optimized to `64` during fine-tuning to smooth out gradient updates and maximize CPU throughput.
- **Phased Training:** Instead of training from scratch, pre-trained ImageNet weights were used. Initial training (Feature Extraction) froze 99.9% of the network, cutting down backpropagation time heavily. 

## 3. Dataset & Pre-processing
The model was trained on the **PlantVillage Dataset**, consisting of 20,638 images spanning 15 categories (Tomato, Potato, and Pepper Bell crops).
- **Splits:** 70% Train, 15% Validation, 15% Test.
- **Augmentations:** To simulate chaotic real-world field environments, the training data underwent Random Resized Cropping, Rotations, Horizontal/Vertical Flipping, and Color Jittering.

## 4. Model Training & Evaluation
The training occurred in two distinct phases:
1. **Feature Extraction (10 Epochs):** Only the final fully connected layer was trained. This achieved a baseline validation accuracy of **78.7%**.
2. **Fine-Tuning (2 Epochs):** The final convolutional block (`layer4`) was unfrozen, adding ~8.4 million trainable parameters. The learning rate was reduced by an order of magnitude. This resulted in a massive performance spike, pushing the model to a **92.75% validation accuracy**.

### Final Test Results
Tested against 3,109 completely unseen test images, the model generalized beautifully, maintaining a **92.0% macro F1-score**. 
- **Strengths:** 98-99% accuracy on distinguishing healthy crops and distinct viral infections (e.g., Yellow Leaf Curl Virus).
- **Weaknesses:** Occasional confusion between visually identical fungal infections (e.g., Tomato Early Blight vs. Target Spot).

## 5. Deployment
The backend PyTorch inference pipeline was encapsulated into a streamlined `predict_image()` function and hooked into a modern **Streamlit Web Interface**. The application is fully responsive, caching the 40MB model weights securely in memory to ensure instantaneous predictions upon user upload. 

## 6. Conclusion
The project successfully proves that highly accurate, production-ready computer vision applications can be developed and deployed entirely on consumer-grade CPU hardware through strategic pipeline optimizations, intelligent downscaling, and transfer learning.
