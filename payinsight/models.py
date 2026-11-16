from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class PayrollEvent(BaseModel):
    employee_id: str
    employer_id: str
    pay_date: date
    gross_pay: Decimal = Field(ge=0)
    net_pay: Decimal = Field(ge=0)
    hours: Decimal = Field(ge=0)
    bank_account_hash: str
    created_at: datetime

class RiskFinding(BaseModel):
    rule_id: str
    severity: Literal["low", "medium", "high", "critical"]
    score: float
    message: str

class EmployeeRisk(BaseModel):
    employee_id: str
    score: float
    band: Literal["low", "medium", "high", "critical"]
    findings: list[RiskFinding]
