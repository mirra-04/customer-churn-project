import os
import sys
import logging

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE5_PATH = os.path.join(PROJECT_ROOT, "phase5")

if PHASE5_PATH not in sys.path:
    sys.path.insert(0, PHASE5_PATH)

from db import engine  # type: ignore


MODELS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "models"
)
LOGISTIC_MODEL_PATH = os.path.join(MODELS_DIR, "logistic_churn.pkl")
TREE_MODEL_PATH = os.path.join(MODELS_DIR, "tree_churn.pkl")


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# RESTRICTED FEATURE SET
#
# WHY: the live /predict-churn endpoint only collects tenure,
# monthly_charges, contract_type, and service_count (matching
# the API5/RE5 briefs exactly -- 4 fields, no more). The
# original ML2 model was trained on 14 features, including
# internet_service, auto_pay_flag, and has_streaming_bundle --
# none of which the endpoint can actually supply. That mismatch
# meant the model was scoring inputs it was never trained to
# receive (forced defaults), which measurably distorted results.
#
# This version trains on ONLY features that can be derived from
# the 4 required inputs, with zero external information:
#   - tenure, monthly_charges, service_count: direct inputs
#   - total_charges: tenure * monthly_charges (deterministic)
#   - high_charge_flag: threshold on monthly_charges (no new info)
#   - is_long_term_customer: threshold on tenure (no new info)
#   - contract_type_*: one-hot of the direct input
#
# The model now matches exactly what production can supply --
# no forced defaults, no out-of-distribution inputs.
# ============================================================

def load_ml_data():

    logger.info("Loading customer_ml_features from MySQL...")

    query = """
        SELECT
            customer_id,
            tenure,
            monthly_charges,
            total_charges,
            service_count,
            high_charge_flag,
            is_long_term_customer,
            contract_type,
            churn
        FROM customer_ml_features
    """

    df = pd.read_sql(query, engine)

    logger.info(f"Rows loaded: {len(df)}")

    return df


def prepare_data(df):

    logger.info("Preparing restricted feature matrix X and target y...")

    y = df["churn"].astype(int)

    X = df.drop(columns=["customer_id", "churn"])

    X = pd.get_dummies(
        X,
        columns=["contract_type"],
        drop_first=False,
        dtype=int
    )

    logger.info(f"X shape: {X.shape}")
    logger.info(f"Feature columns: {list(X.columns)}")

    return X, y


def split_data(X, y):

    logger.info("Splitting data into training and testing sets...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    print("\n" + "=" * 70)
    print("TRAIN / TEST SPLIT")
    print("=" * 70)
    print(f"Training rows : {len(X_train)}")
    print(f"Testing rows  : {len(X_test)}")

    return X_train, X_test, y_train, y_test


def train_logistic(X_train, y_train):
    logger.info("Training Logistic Regression...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model


def train_tree(X_train, y_train):
    logger.info("Training Decision Tree...")
    model = DecisionTreeClassifier(max_depth=5, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, model_name, X_test, y_test, X, y):

    print("\n" + "=" * 70)
    print(model_name.upper())
    print("=" * 70)

    y_pred = model.predict(X_test)

    print("\nCLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred, target_names=["Active", "Churned"]))

    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    cv_scores = cross_val_score(model, X, y, cv=5, scoring="f1")
    cv_f1 = cv_scores.mean()

    print("\n5-FOLD CROSS-VALIDATION F1")
    print(f"Scores : {cv_scores}")
    print(f"Mean CV F1 : {cv_f1:.4f}")

    return {
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision (Churned)": precision,
        "Recall (Churned)": recall,
        "F1 (Churned)": f1,
        "CV F1": cv_f1,
    }


def save_models(logistic_model, tree_model):
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(logistic_model, LOGISTIC_MODEL_PATH)
    joblib.dump(tree_model, TREE_MODEL_PATH)
    logger.info(f"Logistic model saved: {LOGISTIC_MODEL_PATH}")
    logger.info(f"Decision Tree model saved: {TREE_MODEL_PATH}")


def compare_models(results):

    comparison = pd.DataFrame(results)

    print("\n" + "=" * 70)
    print("MODEL COMPARISON (RESTRICTED FEATURE SET)")
    print("=" * 70)
    print(comparison.to_string(index=False))

    best_row = comparison.loc[comparison["F1 (Churned)"].idxmax()]

    print("\n" + "=" * 70)
    print("MODEL SELECTION")
    print("=" * 70)
    print(f"Selected model: {best_row['Model']}")
    print(f"Churned F1: {best_row['F1 (Churned)']:.4f}")


def main():

    print("\n" + "=" * 70)
    print("ML2 RETRAIN -- RESTRICTED FEATURE SET (API-ALIGNED)")
    print("=" * 70)

    try:
        df = load_ml_data()
        X, y = prepare_data(df)
        X_train, X_test, y_train, y_test = split_data(X, y)

        logistic_model = train_logistic(X_train, y_train)
        tree_model = train_tree(X_train, y_train)

        logistic_results = evaluate_model(
            logistic_model, "Logistic Regression", X_test, y_test, X, y
        )
        tree_results = evaluate_model(
            tree_model, "Decision Tree", X_test, y_test, X, y
        )

        compare_models([logistic_results, tree_results])
        save_models(logistic_model, tree_model)

        print("\n" + "=" * 70)
        print("ML2 RETRAIN COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        logger.error(f"ML2 RETRAIN FAILED: {e}")
        raise


if __name__ == "__main__":
    main()