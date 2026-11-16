"""Polars/Pandera validation and payment feature engineering."""
from collections.abc import Iterable

import pandera.polars as pa
import polars as pl

from payinsight.models import PaymentEvent


class PaymentFrameSchema(pa.DataFrameModel):
    transaction_id: str = pa.Field(unique=True)
    merchant_id: str
    customer_id: str
    amount_inr: float = pa.Field(gt=0)
    currency: str = pa.Field(isin=["INR"])
    payment_method: str
    bank_name: str
    transaction_status: str
    city: str
    state: str
    ip_address: str
    device_id: str
    created_at: pl.Datetime(time_zone="UTC")


def payments_frame(events: Iterable[PaymentEvent]) -> pl.DataFrame:
    rows = [event.model_dump() for event in events]
    return pl.DataFrame(rows).with_columns(
        pl.col("amount_inr").cast(pl.Float64),
        pl.col("created_at").cast(pl.Datetime(time_zone="UTC")),
        pl.col("payment_method").cast(pl.String),
        pl.col("bank_name").cast(pl.String),
        pl.col("transaction_status").cast(pl.String),
    ) if rows else pl.DataFrame()


def validate_payments(frame: pl.DataFrame) -> pl.DataFrame:
    PaymentFrameSchema.validate(frame, lazy=True)
    return frame


def build_features(frame: pl.DataFrame) -> pl.DataFrame:
    if frame.is_empty():
        return frame
    return frame.sort("created_at").with_columns(
        pl.col("amount_inr").log1p().alias("amount_log"),
        pl.col("amount_inr").mean().over("merchant_id").alias("merchant_avg_inr"),
        pl.len().over("customer_id").alias("customer_transaction_count"),
        pl.len().over("customer_id").alias("customer_payment_count"),
        pl.col("ip_address").n_unique().over("customer_id").alias("customer_ip_count"),
        (pl.col("transaction_status") == "FAILED").alias("is_failed"),
    ).with_columns(
        (pl.col("amount_inr") > pl.col("merchant_avg_inr") * 3).alias("is_high_amount"),
        (pl.col("customer_transaction_count") >= 8).alias("is_high_velocity"),
    )


def aggregate_metrics(frame: pl.DataFrame) -> dict:
    return {
        "total_transactions": frame.height,
        "successful_transactions": frame.filter(pl.col("transaction_status") == "SUCCESS").height,
        "failed_transactions": frame.filter(pl.col("transaction_status") == "FAILED").height,
        "pending_transactions": frame.filter(pl.col("transaction_status") == "PENDING").height,
        "refunded_transactions": frame.filter(pl.col("transaction_status") == "REFUNDED").height,
        "total_volume_inr": float(frame["amount_inr"].sum() or 0),
        "fraud_rate": 0.0, "merchants": frame["merchant_id"].n_unique(),
        "customers": frame["customer_id"].n_unique(),
    }
