from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.dependencies import get_db
from database.security import verify_api_key

from schemas.churn import ChurnSummaryResponse
from services.churn_service import get_churn_summary

from database.logger import logger

router = APIRouter(
    prefix="/churn",
    tags=["Churn Analytics"]
)


@router.get(
    "/summary",
    response_model=ChurnSummaryResponse
)
def churn_summary(
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    logger.info("GET /churn/summary")

    try:
        return get_churn_summary(db)

    except SQLAlchemyError:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database unavailable",
                "status_code": 500
            }
        )