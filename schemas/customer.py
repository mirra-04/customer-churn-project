from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    customer_id: str
    gender: str
    senior_citizen: int
    partner: int
    dependents: int

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    customer_id: str
    gender: str
    senior_citizen: int
    partner: int
    dependents: int

    model_config = ConfigDict(from_attributes=True)


class CustomerProfileResponse(BaseModel):
    customer_id: str
    gender: str
    senior_citizen: int
    partner: int
    dependents: int

    contract_type: str

    tenure: int
    monthly_charges: Decimal
    total_charges: Decimal | None

    internet_service: str
    payment_method: str

    churn: int

    model_config = ConfigDict(from_attributes=True)