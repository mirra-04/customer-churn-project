"""
One-off repair script: repopulate the `services` table.

Root cause: de3_cleaning.py's build_curated_tables() deletes
`services` (to respect FK order before deleting `customers`)
but never re-inserts into it -- only customers, contracts,
billing, and customer_status get repopulated. This silently
empties `services` on every DE3 run.

Run this once to restore the data now. The permanent fix
(add this insert into de3_cleaning.py) is shown below.
"""

import os
import sys

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PHASE5_PATH = os.path.join(PROJECT_ROOT, "phase5")

if PHASE5_PATH not in sys.path:
    sys.path.insert(0, PHASE5_PATH)

from db import engine  # type: ignore


def repopulate_services():

    df = pd.read_sql("SELECT * FROM cleaned_customers", engine)

    services_df = df[
        [
            "customer_id",
            "phone_service",
            "multiple_lines",
            "internet_service",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
        ]
    ].copy()

    # cleaned_customers stores these as 1/0 (post-CustomerCleaner),
    # but the services table's original columns are VARCHAR
    # (Yes/No/No internet service etc, per SQL1's DDL).
    # multiple_lines / internet_service were never binary-encoded
    # by CustomerCleaner, so they're already text and don't need
    # conversion. The binary ones need converting back.
    binary_service_cols = [
        "phone_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]

    for col in binary_service_cols:
        services_df[col] = services_df[col].map({1: "Yes", 0: "No"})

    with engine.begin() as connection:
        from sqlalchemy import text
        connection.execute(text("DELETE FROM services"))

    services_df.to_sql(
        "services", engine, if_exists="append", index=False
    )

    print(f"services repopulated: {len(services_df)} rows")


if __name__ == "__main__":
    repopulate_services()