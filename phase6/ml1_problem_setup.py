import os
import sys
import logging

import pandas as pd
from sqlalchemy import text


# ============================================================
# IMPORT DATABASE CONNECTION FROM PHASE 5
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE5_PATH = os.path.join(PROJECT_ROOT, "phase5")

if PHASE5_PATH not in sys.path:
    sys.path.insert(0, PHASE5_PATH)

from db import engine  # type: ignore


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# LOAD ML FEATURES
#
# customer_ml_features is now owned entirely by DE4
# (phase5/de4_features.py). ML1's job is problem DEFINITION,
# not feature engineering -- so this script only reads the
# table. It never recomputes or overwrites features, which is
# what caused the earlier feature-definition drift.
# ============================================================

def load_ml_features():

    logger.info(
        "Loading customer_ml_features from MySQL "
        "(built by DE4 -- not rebuilt here)..."
    )

    query = text("""
        SELECT
            customer_id,
            tenure,
            monthly_charges,
            total_charges,
            service_count,
            high_charge_flag,
            is_long_term_customer,
            auto_pay_flag,
            has_streaming_bundle,
            contract_type,
            internet_service,
            churn
        FROM customer_ml_features
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    logger.info(f"Rows loaded: {len(df)}")

    if len(df) == 0:
        raise ValueError(
            "customer_ml_features is empty. Run "
            "phase5/de4_features.py first to build it."
        )

    return df


# ============================================================
# PREPARE X AND Y
# ============================================================

def prepare_ml_data(df):

    logger.info("Preparing X and y...")

    y = df["churn"].astype(int)

    X = df.drop(
        columns=[
            "customer_id",
            "churn"
        ]
    )

    X = pd.get_dummies(
        X,
        columns=[
            "contract_type",
            "internet_service"
        ],
        drop_first=False,
        dtype=int
    )

    return X, y


# ============================================================
# DISPLAY ML1 RESULTS
# ============================================================

def display_results(X, y):

    print("\n" + "=" * 70)
    print("ML1 MACHINE LEARNING PROBLEM DEFINITION")
    print("=" * 70)

    print("\nTARGET:")
    print("churn")

    print("\nDROPPED COLUMN:")
    print("customer_id")

    print("\nNUMERIC FEATURES:")
    numeric_features = [
        "tenure",
        "monthly_charges",
        "total_charges",
        "service_count",
        "high_charge_flag",
        "is_long_term_customer",
        "auto_pay_flag",
        "has_streaming_bundle"
    ]

    for column in numeric_features:
        print(f"  - {column}")

    print("\nCATEGORICAL FEATURES:")
    print("  - contract_type")
    print("  - internet_service")

    print("\nFINAL FEATURE MATRIX X:")
    print(X)

    print("\nTARGET VECTOR y:")
    print(y)

    print("\nSHAPES:")
    print(f"X.shape = {X.shape}")
    print(f"y.shape = {y.shape}")

    print("\nFINAL FEATURE COLUMNS:")

    for column in X.columns:
        print(f"  - {column}")

    print("\nCLASS BALANCE:")
    balance = y.value_counts(
        normalize=True
    ).sort_index()

    print(balance)

    print("\nCLASS COUNTS:")
    print(
        y.value_counts()
        .sort_index()
    )

    print("\nMETRIC DISCUSSION:")
    print(
        "Accuracy should NOT be the primary metric."
    )

    print(
        "A model predicting every customer as "
        "non-churn could achieve about 73% accuracy "
        "without identifying churners."
    )

    print(
        "Recommended primary metrics: "
        "F1-score, precision, and recall for churn=1."
    )

    print("\n" + "=" * 70)
    print("ML1 PROBLEM DEFINITION COMPLETED")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("ML1 CUSTOMER CHURN PREDICTION")
    print("=" * 70)

    try:

        # 1. Load features (built by DE4 -- not rebuilt here)
        df = load_ml_features()

        # 2. Prepare X and y
        X, y = prepare_ml_data(df)

        # 3. Display results
        display_results(X, y)

    except Exception as e:

        logger.error(
            f"ML1 FAILED: {e}"
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()