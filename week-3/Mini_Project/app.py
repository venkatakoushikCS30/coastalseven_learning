import streamlit as st
import joblib
import numpy as np
import pandas as pd

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Loan Approval Predictor",
    page_icon="🏦",
    layout="centered",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .hero {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 2.2rem 1.5rem; border-radius: 18px; text-align: center;
        margin-bottom: 1.8rem; box-shadow: 0 10px 40px rgba(0,0,0,0.30);
        position: relative; overflow: hidden;
    }
    .hero::before {
        content: ""; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(52,211,153,0.08) 0%, transparent 60%);
        pointer-events: none;
    }
    .hero h1 { color: #fff; font-size: 2rem; font-weight: 800; margin: 0; }
    .hero p  { color: #94a3b8; font-size: 0.95rem; margin-top: 0.4rem; }

    .section-title {
        font-size: 0.85rem; font-weight: 700; color: #64748b;
        text-transform: uppercase; letter-spacing: 2px;
        margin: 1.2rem 0 0.4rem; padding-bottom: 0.35rem;
        border-bottom: 2px solid #1e293b;
    }

    .result-card {
        padding: 1.8rem 1.5rem; border-radius: 18px; text-align: center;
        margin-top: 1rem; box-shadow: 0 6px 30px rgba(0,0,0,0.18);
        animation: slideUp 0.45s cubic-bezier(.22,.68,0,1.0);
    }
    .approved { background: linear-gradient(135deg, #065f46, #047857); border: 1px solid #34d399; }
    .rejected { background: linear-gradient(135deg, #7f1d1d, #991b1b); border: 1px solid #f87171; }
    .result-card h2 { color: #fff; font-size: 1.75rem; margin: 0 0 0.3rem; }
    .result-card p  { color: #e2e8f0; font-size: 1rem; margin: 0; }

    .confidence-bar-bg {
        width: 100%; background: rgba(255,255,255,0.15);
        border-radius: 99px; height: 10px; margin-top: 0.8rem; overflow: hidden;
    }
    .confidence-bar-fill { height: 100%; border-radius: 99px; animation: growBar 0.8s ease forwards; }
    .fill-green { background: linear-gradient(90deg, #34d399, #6ee7b7); }
    .fill-red   { background: linear-gradient(90deg, #f87171, #fca5a5); }

    @keyframes slideUp { from { opacity:0; transform:translateY(24px); } to { opacity:1; transform:translateY(0); } }
    @keyframes growBar { from { width:0; } }

    @media (max-width: 768px) {
        .hero { padding: 1.5rem 1rem; border-radius: 14px; }
        .hero h1 { font-size: 1.5rem; }
        .result-card { padding: 1.2rem 1rem; border-radius: 14px; }
        .result-card h2 { font-size: 1.3rem; }
    }
    @media (max-width: 480px) {
        .hero h1 { font-size: 1.25rem; }
        .result-card h2 { font-size: 1.1rem; }
        .section-title { font-size: 0.75rem; }
    }

    div.stButton > button[kind="primary"] {
        border-radius: 12px; font-weight: 600; font-size: 1rem;
        padding: 0.65rem 1.5rem; transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99,102,241,0.35);
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🏦 Loan Approval Predictor</h1>
    <p>Powered by XGBoost · Enter applicant details below</p>
</div>
""", unsafe_allow_html=True)

# ── Load artifacts (cached in memory) ────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    """Load model, feature order, and scaler once and cache across reruns."""
    m = joblib.load("loan_approval_model.pkl")
    f = joblib.load("feature_order.pkl")
    s = joblib.load("scaler.pkl")
    return m, f, s

try:
    model, feature_order, scaler = load_artifacts()
except FileNotFoundError as e:
    st.error(f"❌ File not found: {e}")
    st.stop()

# ── Input Form ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">👤 Personal Details</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    no_of_dependents = st.number_input("No. of Dependents", min_value=0, max_value=10, value=0, step=1)
with col2:
    education = st.selectbox("Education", ["Graduate", "Not Graduate"])
with col3:
    self_employed = st.selectbox("Self Employed", ["No", "Yes"])

st.markdown('<div class="section-title">💰 Financial Details</div>', unsafe_allow_html=True)
col4, col5 = st.columns(2)
with col4:
    income_annum = st.number_input("Annual Income (₹)", min_value=0, value=5_000_000, step=100_000, format="%d")
with col5:
    loan_amount = st.number_input("Loan Amount (₹)", min_value=0, value=10_000_000, step=100_000, format="%d")

col6, col7 = st.columns(2)
with col6:
    loan_term = st.number_input("Loan Term (months)", min_value=1, max_value=360, value=12, step=1)
with col7:
    cibil_score = st.slider("CIBIL Score", min_value=300, max_value=900, value=650, step=1)

st.markdown('<div class="section-title">🏠 Asset Details</div>', unsafe_allow_html=True)
col8, col9 = st.columns(2)
with col8:
    residential_assets = st.number_input("Residential Assets (₹)", min_value=0, value=5_000_000, step=100_000, format="%d")
with col9:
    commercial_assets = st.number_input("Commercial Assets (₹)", min_value=0, value=2_000_000, step=100_000, format="%d")

col10, col11 = st.columns(2)
with col10:
    luxury_assets = st.number_input("Luxury Assets (₹)", min_value=0, value=5_000_000, step=100_000, format="%d")
with col11:
    bank_assets = st.number_input("Bank Assets (₹)", min_value=0, value=3_000_000, step=100_000, format="%d")

# ── Predict ──────────────────────────────────────────────────────────────────
st.markdown("---")

if st.button("🚀  Predict Loan Approval", use_container_width=True, type="primary"):

    # 1. Encode categoricals
    education_enc = 0 if education == "Graduate" else 1
    self_employed_enc = 0 if self_employed == "No" else 1

    # 2. Scale numerical features
    raw_numerics = np.array([[
        income_annum, loan_amount, loan_term, cibil_score,
        residential_assets, commercial_assets, luxury_assets, bank_assets,
    ]])
    s = scaler.transform(raw_numerics)[0]

    # 3. Derived features from scaled values
    total_assets = s[4] + s[5] + s[6] + s[7]
    debt_income_ratio = s[1] / (s[0] + 1)

    # 4. Build DataFrame
    input_data = pd.DataFrame([{
        "no_of_dependents":         no_of_dependents,
        "education":                education_enc,
        "self_employed":            self_employed_enc,
        "income_annum":             s[0],
        "loan_amount":              s[1],
        "loan_term":                s[2],
        "cibil_score":              s[3],
        "residential_assets_value": s[4],
        "commercial_assets_value":  s[5],
        "luxury_assets_value":      s[6],
        "bank_asset_value":         s[7],
        "total_assets":             total_assets,
        "debt_income_ratio":        debt_income_ratio,
    }])[feature_order]

    # 5. Predict
    prediction = model.predict(input_data)[0]
    confidence = model.predict_proba(input_data)[0][prediction] * 100
    status = "Approved" if prediction == 0 else "Rejected"

    # 6. Show result
    if status == "Approved":
        st.markdown(f"""
        <div class="result-card approved">
            <h2>✅ Loan Approved</h2>
            <p>The model predicts this application will be <strong>approved</strong>.</p>
            <p style="margin-top:0.6rem; font-size:0.95rem; color:#a7f3d0;">
                Confidence: <strong>{confidence:.1f}%</strong>
            </p>
            <div class="confidence-bar-bg">
                <div class="confidence-bar-fill fill-green" style="width:{confidence}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-card rejected">
            <h2>❌ Loan Rejected</h2>
            <p>The model predicts this application will be <strong>rejected</strong>.</p>
            <p style="margin-top:0.6rem; font-size:0.95rem; color:#fecaca;">
                Confidence: <strong>{confidence:.1f}%</strong>
            </p>
            <div class="confidence-bar-bg">
                <div class="confidence-bar-fill fill-red" style="width:{confidence}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Input summary
    with st.expander("📋 View input summary"):
        raw_total = residential_assets + commercial_assets + luxury_assets + bank_assets
        raw_dti = loan_amount / (income_annum + 1)
        summary = pd.DataFrame({
            "Field": ["No. of Dependents", "Education", "Self Employed", "Annual Income",
                      "Loan Amount", "Loan Term", "CIBIL Score", "Residential Assets",
                      "Commercial Assets", "Luxury Assets", "Bank Assets",
                      "Total Assets", "Debt-to-Income Ratio"],
            "Value": [str(no_of_dependents), education, self_employed,
                      f"₹{income_annum:,.0f}", f"₹{loan_amount:,.0f}",
                      f"{loan_term} months", str(cibil_score),
                      f"₹{residential_assets:,.0f}", f"₹{commercial_assets:,.0f}",
                      f"₹{luxury_assets:,.0f}", f"₹{bank_assets:,.0f}",
                      f"₹{raw_total:,.0f}", f"{raw_dti:.4f}"],
        })
        st.table(summary)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⚠️ This is a machine-learning prediction tool for educational purposes. Do not use it for actual financial decisions.")
