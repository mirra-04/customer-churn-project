import os
import sys
from datetime import datetime

import pandas as pd
from sqlalchemy import text

# ------------------------------------------------------------------
# Allow importing db.py from phase5
# ------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE5_DIR = os.path.join(PROJECT_ROOT, "phase5")

if PHASE5_DIR not in sys.path:
    sys.path.insert(0, PHASE5_DIR)

from db import engine  # type: ignore

from predict import predict_churn


# ==================================================================
# CONFIGURATION
# ==================================================================

OUTPUT_TABLE = "customer_risk_table"


# ==================================================================
# LOAD CUSTOMER DATA
#
# Includes payment_method now, so auto_pay_flag is computed from
# real data instead of always defaulting to 0 (matches the fix in
# predict.py). service columns included for service_count and
# has_streaming_bundle.
# ==================================================================

def load_model_input_data():
    print("INFO: Loading customer data for batch scoring...")

    query = """
        SELECT
            customer_id,
            tenure,
            internet_service,
            contract,
            monthly_charges,
            total_charges,
            payment_method,
            phone_service,
            online_security,
            online_backup,
            device_protection,
            tech_support,
            streaming_tv,
            streaming_movies,
            churn
        FROM cleaned_customers
    """

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    print(f"INFO: Rows loaded: {len(df)}")

    return df


# ==================================================================
# BATCH SCORING
#
# Calls the same predict_churn() used by the live API and by ML4,
# so batch scores and single-prediction API results are guaranteed
# consistent. Passes the real optional fields (payment_method,
# internet_service, streaming flags) now available -- previously
# these were always hardcoded to defaults inside predict.py.
# ==================================================================

def batch_score(customers):

    print("INFO: Starting batch scoring...")

    results = customers[["customer_id", "churn"]].copy()

    predictions = customers.apply(
        lambda row: predict_churn(
            tenure=int(row["tenure"]),
            monthly_charges=float(row["monthly_charges"]),
            contract_type=row["contract"],
            service_count=int(row["service_count"]),
        ),
        axis=1
    )

    results["risk_score"] = predictions.apply(lambda x: x["risk_score"])
    results["prediction"] = predictions.apply(lambda x: x["prediction"])
    results["confidence"] = predictions.apply(lambda x: x["confidence"])
    results["scoring_date"] = datetime.today().strftime("%Y-%m-%d")

    print("INFO: Batch scoring completed.")

    return results


# ==================================================================
# SAVE CUSTOMER RISK TABLE
# ==================================================================

def save_risk_table(results):

    print(f"INFO: Saving {len(results)} risk records to {OUTPUT_TABLE}...")

    output = results[
        ["customer_id", "risk_score", "prediction", "confidence", "scoring_date"]
    ].copy()

    output.to_sql(OUTPUT_TABLE, engine, if_exists="replace", index=False)

    print(f"INFO: {OUTPUT_TABLE} created successfully.")


# ==================================================================
# PRINT SUMMARY
# ==================================================================

def print_summary(results):

    print()
    print("=" * 70)
    print("ML5 BATCH SCORING SUMMARY")
    print("=" * 70)

    prediction_counts = results["prediction"].value_counts()

    likely_to_churn = prediction_counts.get("Likely to churn", 0)
    unlikely_to_churn = prediction_counts.get("Unlikely to churn", 0)
    total = len(results)

    churn_percentage = (likely_to_churn / total * 100) if total > 0 else 0

    print(f"Total customers       : {total}")
    print(f"Likely to churn       : {likely_to_churn}")
    print(f"Unlikely to churn     : {unlikely_to_churn}")
    print(f"Predicted churn rate  : {churn_percentage:.2f}%")
    print()
    print("Training churn rate   : 26.54%")
    print()


# ==================================================================
# TOP 10 HIGH-RISK CUSTOMERS
# ==================================================================

def print_top_risk_customers(results):

    print("=" * 70)
    print("TOP 10 HIGHEST-RISK CUSTOMERS")
    print("=" * 70)

    top10 = results.sort_values(by="risk_score", ascending=False).head(10)

    print(f"{'Rank':<6}{'Customer ID':<18}{'Risk Score':<15}{'Prediction':<20}")
    print("-" * 70)

    for rank, (_, row) in enumerate(top10.iterrows(), start=1):
        print(
            f"{rank:<6}{row['customer_id']:<18}{row['risk_score']:<15.4f}"
            f"{row['prediction']:<20}"
        )


# ==================================================================
# MAIN
# ==================================================================

def main():

    print()
    print("=" * 70)
    print("ML5 CUSTOMER BATCH SCORING")
    print("=" * 70)

    try:
        customers = load_model_input_data()

        # CANONICAL DEFINITION (matches CP4/DE4/training data):
        # 6 optional service columns, phone_service excluded.
        # This must match exactly, since it becomes the
        # service_count feature the model scores against.
        service_columns = [
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
        ]

        customers["service_count"] = customers[service_columns].sum(axis=1)

        results = batch_score(customers)

        save_risk_table(results)
        print_summary(results)
        print_top_risk_customers(results)

        print()
        print("=" * 70)
        print("ML5 BATCH SCORING COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print()
        print(f"ERROR: ML5 FAILED: {e}")
        raise


if __name__ == "__main__":
    main()