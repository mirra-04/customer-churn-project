import os
import sys

from fastapi import APIRouter, Depends

from database.security import verify_api_key
from database.logger import logger

from schemas.prediction import (
    ChurnPredictionRequest,
    ChurnPredictionResponse,
)


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE6_PATH = os.path.join(PROJECT_ROOT, "phase6")

if PHASE6_PATH not in sys.path:
    sys.path.insert(0, PHASE6_PATH)

from predict import predict_churn  # type: ignore


router = APIRouter(
    tags=["Prediction"]
)


@router.post(
    "/predict-churn",
    response_model=ChurnPredictionResponse,
)
def predict_churn_endpoint(
    request: ChurnPredictionRequest,
    _: None = Depends(verify_api_key),
):
    logger.info(
        f"POST /predict-churn customer={request.customer_id}"
    )

    result = predict_churn(
        tenure=request.tenure,
        monthly_charges=request.monthly_charges,
        contract_type=request.contract_type,
        service_count=request.service_count,
    )

    return {
        "customer_id": request.customer_id or "N/A",
        "risk_score": result["risk_score"],
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "note": "Live prediction from trained Decision Tree model (ML4)",
    }