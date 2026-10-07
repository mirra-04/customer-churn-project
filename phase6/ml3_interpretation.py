import os
import sys
import logging
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split


# ============================================================
# PATH SETUP
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE5_PATH = os.path.join(PROJECT_ROOT, "phase5")

if PHASE5_PATH not in sys.path:
    sys.path.insert(0, PHASE5_PATH)

from db import engine  # type: ignore


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
    "tree_churn.pkl"
)

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "outputs"
)

CHART_PATH = os.path.join(
    OUTPUT_DIR,
    "top_feature_importance.png"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# LOAD FEATURES
#
# IMPORTANT: this now reads customer_ml_features directly --
# the SAME table ML2 trained on -- rather than recomputing
# derived features from cleaned_customers. Recomputing here
# was the root cause of a THIRD, silently inconsistent feature
# definition (different from both CP4 and the DB table).
# Reading the canonical table guarantees ML3's interpretation
# and scoring match what the model actually learned.
# ============================================================

def load_ml_features():

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

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    logger.info(f"Rows loaded: {len(df)}")

    return df


# ============================================================
# PREPARE X AND Y
# ============================================================

def prepare_ml_data(df):

    logger.info("Preparing feature matrix X and target y...")

    df = pd.get_dummies(
        df,
        columns=["contract_type"],
        drop_first=False
    )

    feature_columns = [
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

    missing_columns = [
        col for col in feature_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing expected feature columns:\n"
            + "\n".join(f"  - {col}" for col in missing_columns)
        )

    X = df[feature_columns].copy()
    y = df["churn"].copy()

    logger.info(f"X shape: {X.shape}")
    logger.info(f"y shape: {y.shape}")

    return df, X, y, feature_columns


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    logger.info("Loading Decision Tree model...")

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)

    logger.info("Decision Tree model loaded successfully.")

    return model


# ============================================================
# VALIDATE FEATURES MATCH THE TRAINED MODEL
# ============================================================

def validate_features(model, feature_columns):

    if hasattr(model, "feature_names_in_"):

        model_features = list(model.feature_names_in_)

        if model_features != feature_columns:
            print("\nERROR: Feature mismatch.\n")
            print("Model features:", model_features)
            print("Current features:", feature_columns)
            raise ValueError(
                "ML3 features do not match the trained ML2 model."
            )

    logger.info("Feature validation passed.")


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def analyze_feature_importance(model, feature_columns):

    print("\n" + "=" * 70)
    print("DECISION TREE FEATURE IMPORTANCE")
    print("=" * 70)

    importances = pd.Series(
        model.feature_importances_,
        index=feature_columns
    ).sort_values(ascending=False)

    print("\nALL FEATURE IMPORTANCES:\n")
    for feature, importance in importances.items():
        print(f"{feature:<40} {importance:.6f}")

    top_10 = importances.head(10)

    print("\n" + "=" * 70)
    print("TOP 10 FEATURES")
    print("=" * 70)
    for rank, (feature, importance) in enumerate(top_10.items(), start=1):
        print(f"{rank:2}. {feature:<40} {importance:.6f}")

    top_3 = importances.head(3)

    print("\n" + "=" * 70)
    print("TOP 3 CHURN-ASSOCIATED FEATURES")
    print("=" * 70)
    for rank, (feature, importance) in enumerate(top_3.items(), start=1):
        print(f"{rank}. {feature} (importance={importance:.6f})")

    plt.figure(figsize=(10, 6))
    top_10.sort_values().plot(kind="barh")
    plt.title("Top 10 Feature Importances - Decision Tree")
    plt.xlabel("Feature Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(CHART_PATH, dpi=150)
    plt.close()

    print(f"\nINFO: Feature importance chart saved to:\n{CHART_PATH}")

    return importances


# ============================================================
# TRAIN / TEST SPLIT
#
# Same split parameters as ML2 (test_size=0.2, stratify=y,
# random_state=42) on the same table in the same row order,
# so this reproduces ML2's exact train/test split.
# ============================================================

def create_test_set(X, y, df):

    print("\n" + "=" * 70)
    print("CREATING TEST SET")
    print("=" * 70)

    X_train, X_test, y_train, y_test, df_train, df_test = train_test_split(
        X, y, df,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print(f"\nTraining rows : {len(X_train)}")
    print(f"Testing rows  : {len(X_test)}")

    return X_train, X_test, y_train, y_test, df_train, df_test


# ============================================================
# SCORE HIGH-RISK CUSTOMERS
# ============================================================

def find_high_risk_customers(model, X_test, df_test):

    print("\n" + "=" * 70)
    print("TOP 20 HIGHEST-RISK CUSTOMERS")
    print("=" * 70)

    probabilities = model.predict_proba(X_test)[:, 1]

    results = pd.DataFrame({
        "customer_id": df_test["customer_id"].values,
        "actual_churn": df_test["churn"].values,
        "churn_probability": probabilities
    }).sort_values("churn_probability", ascending=False).reset_index(drop=True)

    top_20 = results.head(20).copy()
    top_20["risk_score"] = (top_20["churn_probability"] * 100).round(2)

    print(f"\n{'Rank':<6}{'Customer ID':<18}{'Actual':<10}{'Risk Score':<12}Churn Probability")
    print("-" * 70)

    for index, row in top_20.iterrows():
        print(
            f"{index + 1:<6}{row['customer_id']:<18}{row['actual_churn']:<10}"
            f"{row['risk_score']:<12}{row['churn_probability']:.4f}"
        )

    risk_path = os.path.join(OUTPUT_DIR, "top_20_high_risk_customers.csv")
    top_20.to_csv(risk_path, index=False)

    print(f"\nINFO: High-risk customer list saved to:\n{risk_path}")

    return top_20, results


# ============================================================
# SQL RULE-BASED HIGH-RISK COMPARISON
# ============================================================

def compare_with_sql_high_risk(top_20):

    print("\n" + "=" * 70)
    print("ML HIGH-RISK VS SQL RULE-BASED HIGH-RISK")
    print("=" * 70)

    try:
        query = "SELECT customer_id FROM v_high_risk_customers"

        with engine.connect() as conn:
            sql_df = pd.read_sql(query, conn)

        sql_ids = set(sql_df["customer_id"])
        ml_ids = set(top_20["customer_id"])
        overlap = ml_ids.intersection(sql_ids)

        print(f"\nSQL high-risk customers : {len(sql_ids)}")
        print(f"ML top-20 customers      : {len(ml_ids)}")
        print(f"Overlap                   : {len(overlap)}")

        if overlap:
            print("\nCustomers appearing in BOTH lists:")
            for customer_id in sorted(overlap):
                print(f"  - {customer_id}")
        else:
            print("\nNo overlap found between the ML top-20 and SQL rule-based list.")
            print(
                "Note: this is not necessarily wrong -- SQL6 flags customers "
                "matching a fixed rule (month-to-month, tenure<12, above-average "
                "charges), while ML ranks by predicted probability across ALL "
                "customers. Low overlap can happen if the model's top risks fall "
                "outside that specific rule (e.g. longer-tenure customers with "
                "other risk factors)."
            )

        overlap_percentage = len(overlap) / len(ml_ids) * 100
        print(f"\nTop-20 ML overlap percentage: {overlap_percentage:.2f}%")

        return overlap

    except Exception as e:
        print("\nWARNING: Could not compare with SQL high-risk list.")
        print(f"Reason: {e}")
        return set()


# ============================================================
# BUSINESS INTERPRETATION
# ============================================================

def print_business_interpretation(importances, top_20):

    print("\n" + "=" * 70)
    print("BUSINESS INTERPRETATION")
    print("=" * 70)

    top_features = list(importances.head(3).index)

    print(
        "\nCustomers most likely to churn are those whose behaviour and "
        "account characteristics align with the strongest predictive "
        "features identified by the Decision Tree."
    )
    print(
        f"The three most influential features are {top_features[0]}, "
        f"{top_features[1]}, and {top_features[2]}."
    )
    print(
        "Retention teams should pay particular attention to customers "
        "showing combinations of these high-risk characteristics."
    )
    print(
        "The model's churn probability provides a way to prioritize "
        "customers instead of treating every customer as equally likely "
        "to leave."
    )
    print(
        "The highest-risk customers can therefore be targeted proactively "
        "with retention offers, service support, or personalized "
        "interventions."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("ML3 MODEL INTERPRETATION")
    print("=" * 70)

    try:
        df = load_ml_features()
        df, X, y, feature_columns = prepare_ml_data(df)
        model = load_model()
        validate_features(model, feature_columns)
        importances = analyze_feature_importance(model, feature_columns)

        X_train, X_test, y_train, y_test, df_train, df_test = create_test_set(X, y, df)

        top_20, all_results = find_high_risk_customers(model, X_test, df_test)
        overlap = compare_with_sql_high_risk(top_20)
        print_business_interpretation(importances, top_20)

        print("\n" + "=" * 70)
        print("ML3 COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nOutputs:")
        print(f"  Feature chart : {CHART_PATH}")
        print(f"  High-risk CSV : {os.path.join(OUTPUT_DIR, 'top_20_high_risk_customers.csv')}")
        print(f"  SQL/ML overlap: {len(overlap)} customers")

    except Exception as e:
        logger.error("ML3 FAILED: %s", e)
        raise


if __name__ == "__main__":
    main()