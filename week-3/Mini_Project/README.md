# 🏦 Loan Approval Prediction System

A machine-learning-powered web application that predicts loan approval outcomes using an **XGBoost classifier** trained on applicant financial and demographic data. Built with **Streamlit** for an interactive, real-time prediction experience.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Dataset](#dataset)
- [Model Pipeline](#model-pipeline)
- [Model Performance](#model-performance)
- [Key Insights](#key-insights)
- [Disclaimer](#disclaimer)

---

## Overview

This project tackles the **binary classification** problem of predicting whether a loan application will be **Approved** or **Rejected**. It covers the full ML lifecycle — from exploratory data analysis and feature engineering to model training, hyperparameter tuning, and deployment as an interactive web app.

---

## ✨ Features

- 🔮 **Real-time Predictions** — Enter applicant details and get instant approval/rejection results with confidence scores
- 📊 **Multiple Models Compared** — Logistic Regression, Decision Tree, Random Forest, and XGBoost
- ⚙️ **Hyperparameter Tuning** — GridSearchCV and RandomizedSearchCV for optimal model selection
- 🎨 **Modern UI** — Sleek dark-themed Streamlit interface with smooth animations and gradient cards
- 📄 **Auto-generated PDF Report** — Comprehensive project report generated programmatically
- 📋 **Input Summary** — Expandable section to review all submitted details after prediction

---

## 🖥️ Demo

Run the app locally and you'll see:

1. A **hero header** with the app title
2. **Input sections** grouped by Personal, Financial, and Asset details
3. A **Predict button** that displays an animated Approved/Rejected card with a confidence bar
4. An expandable **input summary table** for review

---

## 🛠️ Tech Stack

| Category             | Technologies                                                     |
| -------------------- | ---------------------------------------------------------------- |
| **Language**         | Python 3.x                                                       |
| **ML Framework**     | scikit-learn, XGBoost                                            |
| **Data Processing**  | pandas, NumPy                                                    |
| **Visualization**    | Matplotlib, Seaborn                                              |
| **Web App**          | Streamlit                                                        |
| **Serialization**    | Joblib                                                           |
| **Report Generation**| fpdf2                                                            |

---

## 📁 Project Structure

```
Mini_Project/
├── app.py                          # Streamlit web application
├── main.ipynb                      # Jupyter notebook (EDA, training, evaluation)
├── generate_report.py              # Script to generate the PDF project report
├── loan.csv                        # Dataset (4,269 samples, 13 columns)
├── loan_approval_model.pkl         # Trained XGBoost model (serialized)
├── scaler.pkl                      # Fitted StandardScaler for numerical features
├── feature_order.pkl               # Feature name order used during training
├── Loan_Approval_Project_Report.pdf# Auto-generated comprehensive PDF report
└── README.md                       # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Mini_Project
   ```

2. **Install dependencies**

   ```bash
   pip install streamlit pandas numpy scikit-learn xgboost joblib fpdf2 matplotlib seaborn
   ```

3. **Verify the model artifacts exist** — ensure `loan_approval_model.pkl`, `scaler.pkl`, and `feature_order.pkl` are in the project root.

---

## ▶️ Usage

### Run the Web App

```bash
streamlit run app.py
```

The app will open in your browser (typically at `http://localhost:8501`). Fill in the applicant details and click **🚀 Predict Loan Approval**.

### Regenerate the PDF Report

```bash
python generate_report.py
```

This reads the saved model artifacts and dataset to produce `Loan_Approval_Project_Report.pdf`.

### Explore the Notebook

Open `main.ipynb` in Jupyter Notebook or JupyterLab to walk through the full analysis — data exploration, preprocessing, model training, and evaluation.

---

## 📊 Dataset

| Property       | Details                                    |
| -------------- | ------------------------------------------ |
| **Source**      | `loan.csv`                                 |
| **Samples**    | 4,269                                      |
| **Features**   | 13 (including target)                      |
| **Target**     | `loan_status` (Approved / Rejected)        |

### Feature Descriptions

| Feature                     | Type    | Description                              |
| --------------------------- | ------- | ---------------------------------------- |
| `loan_id`                   | int     | Unique identifier (dropped before training) |
| `no_of_dependents`          | int     | Number of dependents                     |
| `education`                 | object  | Graduate / Not Graduate                  |
| `self_employed`             | object  | Yes / No                                 |
| `income_annum`              | int     | Annual income (₹)                        |
| `loan_amount`               | int     | Requested loan amount (₹)               |
| `loan_term`                 | int     | Loan term in months                      |
| `cibil_score`               | int     | Credit score (300–900)                   |
| `residential_assets_value`  | int     | Value of residential assets (₹)         |
| `commercial_assets_value`   | int     | Value of commercial assets (₹)          |
| `luxury_assets_value`       | int     | Value of luxury assets (₹)             |
| `bank_asset_value`          | int     | Value of bank assets (₹)               |
| `loan_status`               | object  | **Target** — Approved / Rejected        |

### Engineered Features

| Feature              | Formula                                            |
| -------------------- | -------------------------------------------------- |
| `total_assets`       | Sum of all 4 asset columns (after scaling)         |
| `debt_income_ratio`  | `loan_amount / (income_annum + 1)` (after scaling) |

---

## ⚙️ Model Pipeline

### 1. Preprocessing

- **Label Encoding** — `education`, `self_employed`, and `loan_status` encoded via `LabelEncoder`
- **Standard Scaling** — 8 numerical features standardized using `StandardScaler`
- **Feature Engineering** — `total_assets` and `debt_income_ratio` derived from scaled values
- **Train/Test Split** — 80/20 split with `stratify=y` and `random_state=42`

### 2. Models Trained

| Model                    | Configuration              |
| ------------------------ | -------------------------- |
| Logistic Regression      | Baseline (`max_iter=1000`) |
| Decision Tree Classifier | Default parameters         |
| Random Forest Classifier | 100 estimators             |
| XGBoost Classifier       | Default parameters         |
| **XGBoost (Tuned)**      | **GridSearchCV optimized** |

### 3. Hyperparameter Tuning

**GridSearchCV** (108 combinations × 3 folds = 324 fits):

| Parameter          | Search Space        |
| ------------------ | ------------------- |
| `n_estimators`     | [100, 200, 300]     |
| `max_depth`        | [3, 5, 7]           |
| `learning_rate`    | [0.01, 0.05, 0.1]   |
| `subsample`        | [0.8, 1.0]          |
| `colsample_bytree` | [0.8, 1.0]          |

**RandomizedSearchCV** was also evaluated with 20 random iterations over a wider search space.

---

## 📈 Model Performance

| Model                | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| -------------------- | :------: | :-------: | :----: | :------: | :-----: |
| Logistic Regression  |  ~89%    |   ~89%    |  ~93%  |   ~91%   |  ~96%   |
| Decision Tree        |  ~98%    |   ~98%    |  ~98%  |   ~98%   |  ~98%   |
| Random Forest        |  ~98%    |   ~99%    |  ~98%  |   ~98%   |  ~99%   |
| XGBoost (Default)    |  ~98%    |   ~98%    |  ~98%  |   ~98%   |  ~99%   |
| **XGBoost (Tuned)**  |**~98%**  | **~98%**  |**~99%**| **~98%** |**~99%** |

> The tuned XGBoost model was selected as the final model based on the best F1-score from GridSearchCV.

---

## 💡 Key Insights

1. **CIBIL Score dominates** — accounts for **73.7%** of feature importance. Scores above ~551 are almost always approved.
2. **Loan Term** is the second most influential feature at **14.8%** importance.
3. Other features (income, assets, education, self-employment) each contribute **< 2%** individually.
4. All tree-based models achieved **~98% accuracy**, indicating strong class separation primarily driven by credit score.

---

## ⚠️ Disclaimer

> This is a **machine-learning prediction tool built for educational purposes only**. It should **not** be used for actual financial or lending decisions. Real-world loan approval involves regulatory, ethical, and contextual factors far beyond the scope of this model.

---


