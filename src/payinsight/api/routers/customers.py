"""Compatibility exports for customer routes mounted by the application."""

from payinsight.api.app import customer_segments, top_transactions

top_customers = top_transactions

__all__ = ["customer_segments", "top_customers"]
