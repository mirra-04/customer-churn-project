import json
import logging
import os

import pandas as pd

from sqlalchemy import create_engine, text
from dotenv import load_dotenv


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# Database Configuration
# ============================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

engine = create_engine(DATABASE_URL)


# ============================================================
# Shared threshold file
#
# The median monthly_charges computed here is the ACTUAL
# threshold used for high_charge_flag. It must be reused
# identically at inference time (predict.py), or the model
# will be scored against a different feature definition than
# it was trained on. This file is the single source of truth
# for that value across DE4 (training-time) and ML4 (inference).
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)  # up from phase5/ to project root

THRESHOLDS_PATH = os.path.join(PROJECT_ROOT, "feature_thresholds.json")


# ============================================================
# Build Features
#
# THIS IS NOW THE SINGLE AUTHORITATIVE BUILDER of
# customer_ml_features. It:
#   1. Uses the EXACT same feature logic as CP4 (median
#      threshold, "automatic" substring match, AND-based
#      streaming bundle, 6-column service_count).
#   2. Includes the extra context columns (tenure,
#      monthly_charges, total_charges, contract_type,
#      internet_service, churn) that ML1/ML2 need, so no
#      other script ever needs to rebuild or duplicate this
#      table with different logic.
#
# ml1_problem_setup.py should only READ this table, never
# rebuild it.
# ============================================================

def build_features(engine):

    logger.info("Reading data from cleaned_customers...")

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    logger.info(
        f"Rows read from cleaned_customers: {len(df)}"
    )

    # ========================================================
    # Feature 1 - Tenure Bucket
    # ========================================================

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
        include_lowest=True
    )

    # ========================================================
    # Feature 2 - High Charge Flag
    #
    # CANONICAL DEFINITION (matches CP4): median-based, not a
    # hardcoded value. The median itself is saved to
    # feature_thresholds.json so predict.py can apply the
    # SAME threshold at inference time.
    # ========================================================

    median_charge = df["monthly_charges"].median()

    logger.info(
        f"Monthly charges median: {median_charge}"
    )

    df["high_charge_flag"] = (
        df["monthly_charges"] > median_charge
    ).astype(int)

    # ========================================================
    # Feature 3 - Service Count
    #
    # CANONICAL DEFINITION (matches CP4): 6 optional service
    # columns. phone_service is intentionally excluded, since
    # CP4 defined this as "optional add-on services", and
    # phone_service is a base subscription almost every
    # customer has.
    # ========================================================

    service_columns = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]

    df["service_count"] = (
        df[service_columns].sum(axis=1)
    )

    # ========================================================
    # Feature 4 - Long Term Customer
    # ========================================================

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)

    # ========================================================
    # Feature 5 - Streaming Bundle
    #
    # CANONICAL DEFINITION (matches CP4): AND logic -- customer
    # must have BOTH streaming_tv and streaming_movies to count
    # as having a "bundle".
    # ========================================================

    df["has_streaming_bundle"] = (
        (df["streaming_tv"] == 1)
        &
        (df["streaming_movies"] == 1)
    ).astype(int)

    # ========================================================
    # Feature 6 - Auto Pay Flag
    #
    # CANONICAL DEFINITION (matches CP4): "automatic" substring
    # match. This correctly excludes "Electronic check", which
    # is NOT an automatic payment method despite superficially
    # looking similar to "Bank transfer (automatic)".
    # ========================================================

    df["auto_pay_flag"] = (
        df["payment_method"]
        .str.contains(
            "automatic",
            case=False,
            na=False
        )
    ).astype(int)

    logger.info("All 6 features generated successfully.")

    # ========================================================
    # Select Required Columns
    #
    # Includes both the engineered features AND the raw
    # context columns (tenure, monthly_charges, total_charges,
    # contract_type, internet_service, churn) that ML1/ML2 need
    # for training. This is the ONE table everything downstream
    # should read from.
    # ========================================================

    df["contract_type"] = df["contract"]

    feature_columns = [
        "customer_id",
        "tenure",
        "monthly_charges",
        "total_charges",
        "tenure_bucket",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag",
        "contract_type",
        "internet_service",
        "churn"
    ]

    features_df = df[feature_columns].copy()

    # ========================================================
    # Write Feature Table
    # ========================================================

    features_df.to_sql(
        "customer_ml_features",
        engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        "customer_ml_features table created successfully."
    )

    # ========================================================
    # Save the median threshold for inference-time reuse
    # ========================================================

    thresholds = {
        "high_charge_flag_median_monthly_charges": float(median_charge)
    }

    with open(THRESHOLDS_PATH, "w") as f:
        json.dump(thresholds, f, indent=2)

    logger.info(
        f"Saved feature thresholds to {THRESHOLDS_PATH}"
    )

    return features_df


# ============================================================
# Validation
# ============================================================

def validate_features(engine):

    logger.info("Running feature validation...")

    # --------------------------------------------------------
    # Row Count Check
    # --------------------------------------------------------

    cleaned_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM cleaned_customers",
        engine
    )["count"].iloc[0]

    feature_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM customer_ml_features",
        engine
    )["count"].iloc[0]

    if cleaned_count == feature_count:
        print(
            f"PASS: Row count check "
            f"({feature_count} == {cleaned_count})"
        )
    else:
        raise AssertionError(
            f"FAIL: Row count mismatch "
            f"({feature_count} != {cleaned_count})"
        )

    # --------------------------------------------------------
    # Feature Column Check
    # --------------------------------------------------------

    expected_columns = [
        "customer_id",
        "tenure",
        "monthly_charges",
        "total_charges",
        "tenure_bucket",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag",
        "contract_type",
        "internet_service",
        "churn"
    ]

    table_columns = pd.read_sql(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'customer_ml_features'
        """,
        engine
    )["COLUMN_NAME"].tolist()

    missing_columns = [
        col
        for col in expected_columns
        if col not in table_columns
    ]

    if missing_columns:
        raise AssertionError(
            f"Missing feature columns: {missing_columns}"
        )

    print("PASS: All expected columns present")

    # --------------------------------------------------------
    # NULL Check (on the engineered/required columns only --
    # total_charges may be legitimately absent for tenure=0
    # customers is already handled upstream by CustomerCleaner,
    # so this should be 0 too)
    # --------------------------------------------------------

    critical_columns = [
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag",
        "churn"
    ]

    feature_df = pd.read_sql(
        "SELECT * FROM customer_ml_features",
        engine
    )

    null_counts = feature_df[critical_columns].isnull().sum()

    if null_counts.sum() == 0:
        print("PASS: No NULL values in critical feature columns")
    else:
        print("FAIL: NULL values found:")
        print(null_counts)

        raise AssertionError(
            "Feature table contains NULL values"
        )

    print("\nFeature validation completed successfully.")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("DE4 FEATURE ENGINEERING PIPELINE (CANONICAL VERSION)")
    print("=" * 60)

    try:

        build_features(engine)

        print("\n")
        print("=" * 60)
        print("DE4 FEATURE VALIDATION")
        print("=" * 60)

        validate_features(engine)

        sample = pd.read_sql(
            "SELECT * FROM customer_ml_features LIMIT 5",
            engine
        )

        print("\nSample feature records:")
        print(sample)

        print("\n")
        print("=" * 60)
        print("DE4 FEATURE PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:

        logger.error(
            f"DE4 FAILED: {e}"
        )

        raise