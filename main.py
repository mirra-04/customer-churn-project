import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers.churn import router as churn_router
from routers.customers import router as customer_router
from routers.features import router as features_router
from routers.high_risk import router as high_risk_router
from routers.prediction import router as prediction_router

from database.logger import logger

# NOTE: routers/churn_summary.py and schemas/churn_summary.py are
# dead code -- an earlier, incomplete draft of API2 superseded by
# routers/churn.py + services/churn_service.py. They were never
# imported here, so removing the files entirely is safe. If you'd
# rather keep them around for reference, that's fine too, but they
# should not be wired into the app.

app = FastAPI(
    title="Customer Retention API",
    version="1.0.0"
)


# ============================================================
# CORS (needed for the React frontend, Phase 4)
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CENTRALIZED REQUEST LOGGING (API6)
#
# Previously each router logged its own request individually.
# This middleware logs every request/response pair in one place,
# including status code and duration, regardless of which route
# handled it -- so no route can be added later and silently skip
# logging.
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration_ms={duration_ms}"
    )

    return response


# ============================================================
# GLOBAL 404 HANDLER (API6)
#
# Routes still return their own structured 404 JSONResponse for
# "resource not found" cases (e.g. unknown customer_id), since
# that's a business-logic 404 with a specific message. This
# handler catches the OTHER kind of 404 -- hitting a path that
# doesn't exist at all -- and makes sure even that returns the
# same consistent ErrorResponse shape instead of FastAPI's
# default HTML/JSON error page.
# ============================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Path not found: {request.url.path}",
            "status_code": 404
        }
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Customer Retention API is running!"
    }


app.include_router(high_risk_router)
app.include_router(customer_router)
app.include_router(churn_router)
app.include_router(features_router)
app.include_router(prediction_router)