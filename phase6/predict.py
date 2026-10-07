import os
import json
import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "tree_churn.pkl")

PROJECT_ROOT = os.path.dirname(BASE_DIR)
THRESHOLDS_PATH = os.path.join(PROJECT_ROOT, "feature_thresholds.json")


# ============================================================
# LOAD MODEL ONCE AT MODULE LEVEL
# ============================================================

print("INFO: Loading Decision Tree churn model...")
model = joblib.load(MODEL_PATH)
print("INFO: Decision Tree model loaded successfully.")


# ============================================================
# LOAD THE CANONICAL THRESHOLD USED AT TRAINING TIME
# ============================================================

if not os.path.exists(THRESHOLDS_PATH):
    raise FileNotFoundError(
        f"feature_thresholds.json not found at {THRESHOLDS_PATH}. "
        "Run phase5/de4_features.py first to generate it."
    )

with open(THRESHOLDS_PATH) as f:
    _thresholds = json.load(f)

HIGH_CHARGE_MEDIAN = _thresholds["high_charge_flag_median_monthly_charges"]

print(f"INFO: Using high_charge_flag threshold: {HIGH_CHARGE_MEDIAN}")


# ============================================================
# TRAINING FEATURE COLUMNS
#
# RESTRICTED SET: every one of these is derivable from the 4
# required inputs alone (tenure, monthly_charges, contract_type,
# service_count), with zero additional real-world information.
# This matches ml2_model_training_restricted.py exactly, and
# means the model is never asked to score on defaulted/guessed
# values -- what it was trained on is exactly what it receives.
# ============================================================

FEATURE_COLUMNS = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "contract_type_Month-to-month",
    "contract_type_One year",
    "contract_type_Two year",
]


# ============================================================
# PREPROCESS INPUT
# ============================================================

def preprocess_input(tenure, monthly_charges, contract_type, service_count):

    total_charges = tenure * monthly_charges

    high_charge_flag = int(monthly_charges > HIGH_CHARGE_MEDIAN)

    is_long_term_customer = int(tenure >= 24)

    contract_type_month_to_month = int(contract_type == "Month-to-month")
    contract_type_one_year = int(contract_type == "One year")
    contract_type_two_year = int(contract_type == "Two year")

    data = {
        "tenure": [tenure],
        "monthly_charges": [monthly_charges],
        "total_charges": [total_charges],
        "service_count": [service_count],
        "high_charge_flag": [high_charge_flag],
        "is_long_term_customer": [is_long_term_customer],
        "contract_type_Month-to-month": [contract_type_month_to_month],
        "contract_type_One year": [contract_type_one_year],
        "contract_type_Two year": [contract_type_two_year],
    }

    df = pd.DataFrame(data)
    df = df[FEATURE_COLUMNS]

    return df


# ============================================================
# PREDICTION FUNCTION
#
# risk_score and confidence are 0-1 fractions.
# ============================================================

def predict_churn(tenure, monthly_charges, contract_type, service_count):

    X = preprocess_input(
        tenure=tenure,
        monthly_charges=monthly_charges,
        contract_type=contract_type,
        service_count=service_count,
    )

    prediction = int(model.predict(X)[0])

    probabilities = model.predict_proba(X)[0]
    churn_probability = float(probabilities[1])

    risk_score = round(churn_probability, 4)

    prediction_text = "Likely to churn" if prediction == 1 else "Unlikely to churn"

    confidence = round(max(float(probabilities[0]), float(probabilities[1])), 4)

    return {
        "risk_score": risk_score,
        "prediction": prediction_text,
        "confidence": confidence,
    }