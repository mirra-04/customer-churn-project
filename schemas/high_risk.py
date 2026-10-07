from pydantic import BaseModel, ConfigDict


class HighRiskCustomerResponse(BaseModel):
    customer_id: str
    gender: str
    contract_type: str
    tenure: int
    monthly_charges: float
    internet_service: str
    churn: int
    risk_reason: str

    model_config = ConfigDict(from_attributes=True)