import os
from pathlib import Path

# Base Directories
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "dataset"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TRAIN_PATH = PROCESSED_DATA_DIR / "train.csv"
VAL_PATH = PROCESSED_DATA_DIR / "val.csv"
TEST_PATH = PROCESSED_DATA_DIR / "test.csv"
LABEL_MAPS_PATH = PROCESSED_DATA_DIR / "label_maps.json"

# Model Directories
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "faq_intent_model"

# Report Directories
REPORTS_DIR = PROJECT_ROOT / "reports"
CONFUSION_MATRIX_PATH = REPORTS_DIR / "confusion_matrix.png"
EVAL_REPORT_PATH = REPORTS_DIR / "evaluation_report.json"

# Model Parameters
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 128
SEED = 42

# Ensure paths exist
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
