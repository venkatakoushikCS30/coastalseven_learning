# Plant Disease Detection — Project Knowledge

> **Single source of truth.** Every factual metric, hardware spec, and dataset
> stat recorded here comes from actual script execution — never fabricated.

---

## Phase 0 — Hardware & Environment

*Status: COMPLETE*

### Hardware Detected

| Component       | Value                                                    |
|-----------------|----------------------------------------------------------|
| CPU Model       | Intel64 Family 6 Model 186 Stepping 2, GenuineIntel     |
| Architecture    | AMD64                                                    |
| Physical Cores  | 8                                                        |
| Logical Cores   | 12                                                       |
| RAM (Total)     | 15.67 GB                                                 |
| RAM (Available) | ~3.4 GB (varies at runtime)                              |
| GPU             | **None** — No CUDA GPU detected                         |
| Storage (Total) | 474.53 GB                                                |
| Storage (Free)  | ~290 GB                                                  |

### Software Environment

| Package         | Version        |
|-----------------|----------------|
| Python          | 3.11.9         |
| OS              | Windows 10     |
| PyTorch         | 2.12.0+cpu     |
| torchvision     | 0.27.0+cpu     |

### Derived Hyperparameters

| Parameter               | Value   |
|-------------------------|---------|
| image_size              | 128     |
| batch_size              | 16      |
| epochs_feature_extract  | 10      |
| epochs_finetune         | 10      |
| num_workers             | 4       |
| lr_feature_extract      | 0.001   |
| lr_finetune             | 0.0001  |
| use_amp                 | False   |
| device                  | cpu     |

> **Note:** No GPU available. Training will use CPU only. AMP disabled.
> Image size reduced to 128px and batch size to 16 for feasible CPU training.

---

## Phase 1 — Dataset Analysis

*Status: COMPLETE*

### Dataset Location

`C:\Users\koushik\Desktop\Mini_Project_DL\PlantVillage`

### Summary

| Metric         | Value   |
|----------------|---------|
| Num classes    | 15      |
| Total images   | 20,638  |
| Most common    | Tomato__Tomato_YellowLeaf__Curl_Virus (3,208) |
| Least common   | Potato___healthy (152)                         |

### Per-Class Counts

| Class Name                                    | Count |
|-----------------------------------------------|-------|
| Pepper__bell___Bacterial_spot                 | 997   |
| Pepper__bell___healthy                        | 1,478 |
| Potato___Early_blight                         | 1,000 |
| Potato___Late_blight                          | 1,000 |
| Potato___healthy                              | 152   |
| Tomato_Bacterial_spot                         | 2,127 |
| Tomato_Early_blight                           | 1,000 |
| Tomato_Late_blight                            | 1,909 |
| Tomato_Leaf_Mold                              | 952   |
| Tomato_Septoria_leaf_spot                     | 1,771 |
| Tomato_Spider_mites_Two_spotted_spider_mite   | 1,676 |
| Tomato__Target_Spot                           | 1,404 |
| Tomato__Tomato_YellowLeaf__Curl_Virus         | 3,208 |
| Tomato__Tomato_mosaic_virus                   | 373   |
| Tomato_healthy                                | 1,591 |

### Train/Val/Test Split (70/15/15, seed=42, stratified)

| Split | Count  |
|-------|--------|
| Train | 14,440 |
| Val   | 3,089  |
| Test  | 3,109  |

> **Note:** Class imbalance present — ratio of largest to smallest class is ~21:1
> (YellowLeaf Curl Virus 3,208 vs Potato healthy 152).

---

## Phase 2 — Augmentations

*Status: COMPLETE*

### Training Transforms (7 steps)

| # | Transform           | Config                                          |
|---|---------------------|-------------------------------------------------|
| 0 | RandomResizedCrop   | size=128, scale=(0.8, 1.0), bilinear            |
| 1 | RandomHorizontalFlip| p=0.5                                           |
| 2 | RandomVerticalFlip  | p=0.5                                           |
| 3 | RandomRotation      | degrees=[-15, 15]                               |
| 4 | ColorJitter         | brightness=0.2, contrast=0.2, sat=0.2, hue=0.1 |
| 5 | ToTensor            | [0,1] float                                     |
| 6 | Normalize           | ImageNet mean/std                               |

### Val / Test Transforms (4 steps, deterministic)

| # | Transform   | Config                      |
|---|-------------|-----------------------------|
| 0 | Resize      | 145 (1.14x overshoot)       |
| 1 | CenterCrop  | 128x128                     |
| 2 | ToTensor    | [0,1] float                 |
| 3 | Normalize   | ImageNet mean/std           |

Output tensor shape: `[3, 128, 128]` — verified on dummy image.

---

## Phase 3 — Transfer Learning Setup

*Status: COMPLETE*

### Architecture

- **Backbone:** ResNet18 (ImageNet pre-trained, `ResNet18_Weights.IMAGENET1K_V1`)
- **Head:** `Dropout(0.3)` → `Linear(512, 15)`
- **Input shape:** `[B, 3, 128, 128]`
- **Output shape:** `[B, 15]`

### Parameter Summary

| Mode                             | Total       | Trainable     | Frozen        |
|----------------------------------|-------------|---------------|---------------|
| Feature Extraction (Phase 4)     | 11,184,207  | 7,695 (0.1%)  | 11,176,512 (99.9%) |
| Fine-Tune layer4 (Phase 5)       | 11,184,207  | 8,401,423 (75.1%) | 2,782,784 (24.9%) |

### Trainable Layers (Feature Extraction Mode)

| Layer       | Params |
|-------------|--------|
| fc.1.weight | 7,680  |
| fc.1.bias   | 15     |

> Forward pass verified with dummy input `[2, 3, 128, 128]` → output `[2, 15]`.

---

## Phase 4 — Training (Feature Extraction)

*Status: COMPLETE*

### Training Run Details
- **Mode:** Feature extraction (only classification head was trained)
- **Epochs run:** 10
- **Elapsed time:** 2,419.1 seconds (~40.3 minutes on CPU)

### Final Metrics
| Metric | Value |
|--------|-------|
| Best Epoch | 6 |
| Best Val Acc | **78.70%** (0.7870) |
| Best Val Loss | 0.6859 |
| Final Train Acc | 66.57% (0.6657) |
| Final Train Loss| 1.0252 |

> **Note:** The validation accuracy outperformed training accuracy, which is common when using heavy data augmentation on the training set (RandomResizedCrop, ColorJitter, etc.).

### Artifacts
- **Checkpoint:** `models/best_feature_extract.pth`
- **History:** `models/history_feature_extract.json`

---

## Phase 5 — Fine-Tuning

*Status: COMPLETE*

### Fine-Tuning Run Details
- **Mode:** Fine-tuning (unfroze ResNet `layer4` + classification head)
- **Epochs run:** 2 (reduced to save time based on rapid convergence)
- **Learning rate:** `1e-4` (reduced from `1e-3`)
- **Elapsed time:** 1,371.5 seconds (~22.8 minutes on CPU)

### Performance Comparison: Phase 4 vs. Phase 5
| Metric | Phase 4 (Feature Ext.) | Phase 5 (Fine-Tuning) | Improvement |
|--------|------------------------|-----------------------|-------------|
| **Best Val Accuracy** | 78.70% | **92.75%** | **+14.05%** 🚀 |
| **Final Train Accuracy** | 66.57% | 88.41% | +21.84% |
| **Best Val Loss** | 0.6859 | **0.2140** | -0.4719 |
| **Trainable Params** | ~7.6k | ~8.4M | N/A |

> **Conclusion:** Unfreezing the final convolutional block of ResNet18 and training with a lower learning rate yielded a massive **14% boost** in validation accuracy. The model has highly specialized its feature extraction for plant diseases.

### Artifacts
- **Checkpoint:** `models/best_finetune.pth`
- **History:** `models/history_finetune.json`

## Phase 6 — Evaluation

*Status: COMPLETE*

### Results on Untouched Test Set
- **Test Accuracy:** 92% (0.92) across 3,109 images
- **Macro Avg (Precision/Recall/F1):** 0.92 / 0.92 / 0.92
- **Weighted Avg (Precision/Recall/F1):** 0.92 / 0.92 / 0.92

### Notable Class Performances
- **Highest Accuracy (F1-score 0.98–0.99):** `Tomato_healthy`, `Tomato__Tomato_YellowLeaf__Curl_Virus`, `Pepper__bell___healthy`
- **Lowest Accuracy (F1-score 0.77):** `Tomato_Early_blight` (often visually confused with other blights or spots)

### Artifacts Generated
- **Classification Report:** `results/classification_report.txt`
- **Confusion Matrix:** `results/confusion_matrix.png`

---

## Phase 7 — Inference & Export

*Status: COMPLETE*

### Implementation
- **Script:** `src/inference.py`
- **Core Function:** `predict_image(image_path, model, transform, class_names, device)`
- The function handles loading the image, applying deterministic validation transforms, running the forward pass without gradients, and calculating the softmax confidence score.

### Sanity Check Results
Tested on 3 randomly sampled images from the untouched Test set:
1. `Tomato_Septoria_leaf_spot` — Predicted correctly (Confidence: 99.8%)
2. `Potato___Early_blight` — Predicted correctly (Confidence: 100.0%)
3. `Pepper__bell___Bacterial_spot` — Predicted correctly (Confidence: 93.6%)

---

## Phase 8 — Web App (Streamlit)

*Status: COMPLETE*

### Implementation Details
- Built an interactive Streamlit UI (`app.py`).
- Implemented file uploading for plant leaf pictures (JPG/PNG).
- Integrated the `predict_image` function from Phase 7 directly, accepting in-memory PIL images.
- Used `@st.cache_resource` for efficient model loading, preventing the weights from reloading on every interaction.
- Styled with custom HTML/CSS to visually distinguish "Healthy" predictions (green) from "Disease" predictions (red alerts).



---

## Phase 9 — Model Card & Presentation

*Status: COMPLETE*

- Created `MODEL_CARD.md` which thoroughly documents the model's architecture, training data, performance metrics, and ethical limitations/biases (e.g. laboratory conditions vs real-world environments).

---

## Phase 10 — Final Report

*Status: COMPLETE*

- Generated the capstone `final_report.md`, summarizing the entire deep learning pipeline, dataset splits, phased CPU optimization strategies, high-level evaluation metrics (92.0% accuracy), and Streamlit deployment.
