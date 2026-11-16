"""Typed ingestion, quality checks, and feature engineering in Polars."""
from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

import pandera.polars as pa
import polars as pl

from payinsight.models import PaymentEvent


class PaymentFrameSchema(pa.DataFrameModel):
    payment_id: str = pa.Field(unique=True)
    merchant_id: str
    customer_id: str
    amount: float = pa.Field(gt=0)
    currency: str = pa.Field(isin=["USD", "EUR", "GBP", "CAD", "AUD", "SGD"])
    status: str
    payment_method: str
    merchant_category: str
    country: str
    ip_address: str
    device_id: str
    created_at: pl.Datetime(time_zone="UTC")

    class Config:
        strict = False


def payments_frame(events: Iterable[PaymentEvent]) -> pl.DataFrame:
    """Convert domain events to a columnar frame with stable types."""
    rows = [event.model_dump() for event in events]
    if not rows:
        return pl.DataFrame(
            schema={
                "payment_id": pl.String,
                "merchant_id": pl.String,
                "customer_id": pl.String,
                "amount": pl.Float64,
                "currency": pl.String,
                "status": pl.String,
                "payment_method": pl.String,
                "merchant_category": pl.String,
                "country": pl.String,
                "ip_address": pl.String,
                "device_id": pl.String,
                "created_at": pl.Datetime(time_zone="UTC"),
            }
        )
    return pl.DataFrame(rows).with_columns(
        pl.col("amount").cast(pl.Float64),
        pl.col("created_at").cast(pl.Datetime(time_zone="UTC")),
        pl.col("status").cast(pl.String),
        pl.col("payment_method").cast(pl.String),
    )


def validate_payments(frame: pl.DataFrame) -> pl.DataFrame:
    """Validate a frame and return it unchanged when it meets the contract."""
    PaymentFrameSchema.validate(frame, lazy=True)
    return frame


def build_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Add model-ready velocity, amount, and geography features."""
    if frame.is_empty():
        return frame.with_columns(
            pl.lit(0).cast(pl.Int64).alias("customer_payment_count"),
            pl.lit(0.0).alias("customer_total_amount"),
            pl.lit(False).alias("is_high_amount"),
        )
    return (
        frame.sort("created_at")
        .with_columns(
            pl.col("amount").log1p().alias("amount_log"),
            pl.col("amount").mean().over("merchant_id").alias("merchant_avg_amount"),
            pl.len().over("customer_id").alias("customer_payment_count"),
            pl.col("amount").sum().over("customer_id").alias("customer_total_amount"),
            pl.col("ip_address").n_unique().over("customer_id").alias("customer_ip_count"),
        )
        .with_columns(
            (pl.col("amount") > pl.col("merchant_avg_amount") * 3).alias("is_high_amount"),
            (pl.col("customer_payment_count") >= 5).alias("is_high_velocity"),
        )
    )


def aggregate_metrics(frame: pl.DataFrame) -> dict[str, int | float]:
    """Return dashboard-safe aggregate metrics."""
    return {
        "total_payments": frame.height,
        "successful_payments": frame.filter(pl.col("status") == "succeeded").height,
        "failed_payments": frame.filter(pl.col("status") == "failed").height,
        "total_volume": float(frame["amount"].sum() or Decimal(0)),
        "merchants": frame["merchant_id"].n_unique(),
        "customers": frame["customer_id"].n_unique(),
    }
