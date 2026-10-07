from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.dependencies import get_db
from database.security import verify_api_key
from schemas.features import CustomerFeaturesResponse

from database.logger import logger


router = APIRouter(
    prefix="/features",
    tags=["Customer Features"]
)


@router.get(
    "/{customer_id}",
    response_model=CustomerFeaturesResponse
)
def get_customer_features(
    customer_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    logger.info(
        f"GET /features/{customer_id}"
    )
    try:
        # FIXED: previously joined Billing/Contract/Service directly
        # and returned raw customer details (contract_type, payment
        # method, etc) instead of the actual ML feature vector. Now
        # reads from customer_ml_features -- the table ML1/ML2/ML3
        # actually use -- matching the API4 brief exactly.
        result = db.execute(
            text("""
                SELECT
                    customer_id,
                    tenure,
                    monthly_charges,
                    total_charges,
                    service_count,
                    high_charge_flag,
                    is_long_term_customer,
                    auto_pay_flag,
                    has_streaming_bundle
                FROM customer_ml_features
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        )

        row = result.first()

        if row is None:
            return JSONResponse(
                status_code=404,
                content={
                    "detail": "Customer not found",
                    "status_code": 404
                }
            )

        return {
            "customer_id": row.customer_id,
            "tenure": row.tenure,
            "monthly_charges": float(row.monthly_charges),
            "total_charges": float(row.total_charges) if row.total_charges is not None else None,
            "service_count": row.service_count,
            "high_charge_flag": row.high_charge_flag,
            "is_long_term_customer": row.is_long_term_customer,
            "auto_pay_flag": row.auto_pay_flag,
            "has_streaming_bundle": row.has_streaming_bundle,
        }

    except SQLAlchemyError:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database unavailable",
                "status_code": 500
            }
        )