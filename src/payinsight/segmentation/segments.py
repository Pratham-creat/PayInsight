import polars as pl


def segment_customers(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.with_columns(
        pl.when(pl.col("customer_transaction_count") >= 8)
        .then(pl.lit("high_frequency"))
        .when(pl.col("amount_inr") >= 50_000)
        .then(pl.lit("high_value"))
        .otherwise(pl.lit("standard"))
        .alias("customer_segment")
    )
