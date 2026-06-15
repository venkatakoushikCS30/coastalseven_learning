# 🌿 Plant Disease Detection with ResNet18

End-to-end deep learning pipeline for classifying plant leaf diseases using
transfer learning on the **PlantVillage** dataset.

## Project Structure

```
plant-disease-resnet18/
├── data/                  # PlantVillage dataset (downloaded at runtime)
├── configs/
│   └── hw_config.yaml     # Auto-generated hardware & hyper-param config
├── src/
│   ├── hardware_check.py  # Phase 0 — detect hardware, generate config
│   ├── dataset.py         # Phase 1 — dataset loading & analysis
│   ├── augmentations.py   # Phase 2 — train / val / test transforms
│   ├── model.py           # Phase 3 — ResNet18 transfer learning setup
│   ├── train.py           # Phase 4/5 — training & fine-tuning
│   ├── evaluate.py        # Phase 6 — metrics, confusion matrix
│   └── inference.py       # Phase 7 — inference helper
├── app.py                 # Phase 8 — Streamlit Web App
├── models/                # Exported model artifacts
├── results/               # Plots and visualizations
├── project_knowledge.md   # Living document of factual results
├── MODEL_CARD.md          # Phase 9
├── final_report.md        # Phase 10
├── requirements.txt
└── .gitignore
```

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv && venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run hardware check (Phase 0)
python src/hardware_check.py
```
