"""Compatibility exports for transaction routes mounted by the application."""

from payinsight.api.app import transaction, transactions

__all__ = ["transactions", "transaction"]
