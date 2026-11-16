"""PayInsight's Indian payment domain models.

``is_fraud`` is deliberately an ingestion/model-training field and is never part of
the public response models.
"""
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TransactionStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    REFUNDED = "REFUNDED"


class PaymentMethod(StrEnum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class BankName(StrEnum):
    HDFC = "HDFC Bank"
    SBI = "State Bank of India"
    ICICI = "ICICI Bank"
    AXIS = "Axis Bank"
    KOTAK = "Kotak Mahindra Bank"
    YES = "Yes Bank"
    IDFC = "IDFC First Bank"
    PNB = "Punjab National Bank"


class PaymentEvent(BaseModel):
    """Canonical generated row. Amounts are always Indian rupees."""

    model_config = ConfigDict(from_attributes=True)
    transaction_id: str = Field(pattern=r"^txn_[a-z0-9]{12}$")
    payment_id: str | None = None  # compatibility alias for prior clients
    merchant_id: str = Field(pattern=r"^mer_[A-Z0-9]{6}$")
    customer_id: str = Field(pattern=r"^cus_[A-Z0-9]{6}$")
    amount_inr: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(default="INR", pattern="^INR$")
    payment_method: PaymentMethod
    bank_name: BankName
    transaction_status: TransactionStatus
    status: TransactionStatus | None = None
    merchant_category: str
    city: str
    state: str
    ip_address: str
    device_id: str
    created_at: datetime
    is_fraud: bool = False
    fraud_type: str | None = None
    retry_of: str | None = None
    response_code: str | None = None
    failure_reason: str | None = None
    bank_outage: bool = False
    dirty_row: bool = False

    @property
    def amount(self) -> Decimal:
        """Compatibility accessor; canonical storage name is amount_inr."""
        return self.amount_inr

    def public_dict(self) -> dict:
        """Return a safe representation, excluding labels and internal fields."""
        return self.model_dump(
            mode="json",
            exclude={"is_fraud", "fraud_type", "payment_id", "status"},
        )


class RiskFinding(BaseModel):
    rule_id: str
    severity: str
    score: float = Field(ge=0, le=100)
    message: str
    evidence: dict[str, str | int | float] = {}


class PaymentRisk(BaseModel):
    transaction_id: str
    risk_score: float = Field(ge=0, le=100)
    risk_band: str
    decision: str
    findings: list[RiskFinding]


class Metrics(BaseModel):
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    refunded_transactions: int
    total_volume_inr: float
    fraud_rate: float
    high_risk_transactions: int
    merchants: int
    customers: int
    # Deprecated response keys retained for one release for dashboard clients.
    total_payments: int | None = None
    successful_payments: int | None = None
    failed_payments: int | None = None
    total_volume: float | None = None


class KPI(BaseModel):
    name: str
    value: float
    unit: str
    description: str
