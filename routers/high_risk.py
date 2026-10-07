from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.dependencies import get_db
from database.security import verify_api_key
from schemas.high_risk import HighRiskCustomerResponse

from database.logger import logger

router = APIRouter(
    prefix="/customers",
    tags=["High Risk Customers"]
)


@router.get(
    "/high-risk",
    response_model=list[HighRiskCustomerResponse]
)
def get_high_risk_customers(
    limit: int = Query(50, ge=1, le=500),
    min_tenure: Optional[int] = Query(None, ge=0),
    max_tenure: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    logger.info(
        f"GET /customers/high-risk limit={limit} "
        f"min_tenure={min_tenure} max_tenure={max_tenure}"
    )

    try:
        query = "SELECT * FROM v_high_risk_customers WHERE 1=1"
        params = {}

        if min_tenure is not None:
            query += " AND tenure >= :min_tenure"
            params["min_tenure"] = min_tenure

        if max_tenure is not None:
            query += " AND tenure <= :max_tenure"
            params["max_tenure"] = max_tenure

        query += " ORDER BY monthly_charges DESC LIMIT :limit"
        params["limit"] = limit

        result = db.execute(text(query), params)

        customers = []

        for row in result:
            customers.append({
                "customer_id": row.customer_id,
                "gender": row.gender,
                "contract_type": row.contract_type,
                "tenure": row.tenure,
                "monthly_charges": float(row.monthly_charges),
                "internet_service": row.internet_service,
                "churn": row.churn,
                "risk_reason": row.risk_reason,
            })

        return customers

    except SQLAlchemyError:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database unavailable",
                "status_code": 500
            }
        )