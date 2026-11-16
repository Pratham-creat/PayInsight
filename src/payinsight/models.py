"""Validated domain models shared by ingestion, risk, and the API."""
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class PaymentStatus(StrEnum):
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"
    pending = "pending"


class PaymentMethod(StrEnum):
    card = "card"
    bank_transfer = "bank_transfer"
    wallet = "wallet"


class PaymentEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: str = Field(pattern=r"^pay_[a-z0-9]{12}$")
    merchant_id: str = Field(pattern=r"^mer_[A-Z0-9]{6}$")
    customer_id: str = Field(pattern=r"^cus_[A-Z0-9]{6}$")
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    status: PaymentStatus
    payment_method: PaymentMethod
    merchant_category: str = Field(min_length=2, max_length=40)
    country: str = Field(min_length=2, max_length=2)
    ip_address: str
    device_id: str = Field(min_length=8, max_length=64)
    created_at: datetime


class RiskFinding(BaseModel):
    rule_id: str
    severity: str
    score: float = Field(ge=0, le=100)
    message: str
    evidence: dict[str, str | int | float] = {}


class PaymentRisk(BaseModel):
    payment_id: str
    risk_score: float = Field(ge=0, le=100)
    risk_band: str
    decision: str
    findings: list[RiskFinding]


class Metrics(BaseModel):
    total_payments: int
    successful_payments: int
    failed_payments: int
    total_volume: float
    high_risk_payments: int
    merchants: int
    customers: int
