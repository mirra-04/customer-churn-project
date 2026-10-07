"""
Run this from phase6/ (same folder as predict.py):
    python test_predictions.py

Prints the actual model output for each test case so you can
compare against the expected direction.
"""

from predict import predict_churn

test_cases = [
    {"name": "1. Short tenure, month-to-month, high charges",
     "tenure": 2, "monthly_charges": 95, "contract_type": "Month-to-month",
     "service_count": 1, "expected": "HIGH risk"},

    {"name": "2. Brand new, month-to-month, no services",
     "tenure": 1, "monthly_charges": 90, "contract_type": "Month-to-month",
     "service_count": 0, "expected": "HIGH risk"},

    {"name": "3. Long tenure, two-year contract",
     "tenure": 70, "monthly_charges": 90, "contract_type": "Two year",
     "service_count": 5, "expected": "LOW risk"},

    {"name": "4. Long tenure, two-year, fully loaded",
     "tenure": 65, "monthly_charges": 60, "contract_type": "Two year",
     "service_count": 6, "expected": "LOW risk"},

    {"name": "5. Short-ish tenure but one-year contract",
     "tenure": 5, "monthly_charges": 50, "contract_type": "One year",
     "service_count": 2, "expected": "LOW-MEDIUM risk"},

    {"name": "6. Mid tenure, month-to-month",
     "tenure": 40, "monthly_charges": 80, "contract_type": "Month-to-month",
     "service_count": 3, "expected": "MEDIUM risk"},

    {"name": "7. Very low charges, month-to-month, new",
     "tenure": 1, "monthly_charges": 20, "contract_type": "Month-to-month",
     "service_count": 0, "expected": "Uncertain -- tests charges weight"},

    {"name": "8. Boundary: tenure=24, month-to-month",
     "tenure": 24, "monthly_charges": 70, "contract_type": "Month-to-month",
     "service_count": 4, "expected": "Uncertain -- tests tenure boundary"},
]

print(f"{'Test':<50}{'Risk Score':<12}{'Prediction':<20}{'Expected'}")
print("-" * 110)

for case in test_cases:
    result = predict_churn(
        tenure=case["tenure"],
        monthly_charges=case["monthly_charges"],
        contract_type=case["contract_type"],
        service_count=case["service_count"],
    )

    print(
        f"{case['name']:<50}"
        f"{result['risk_score']:<12}"
        f"{result['prediction']:<20}"
        f"{case['expected']}"
    )