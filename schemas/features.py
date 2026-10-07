from pydantic import BaseModel


class CustomerFeaturesResponse(BaseModel):
    customer_id: str
    tenure: int
    monthly_charges: float
    total_charges: float | None
    service_count: int
    high_charge_flag: int
    is_long_term_customer: int
    auto_pay_flag: int
    has_streaming_bundle: int