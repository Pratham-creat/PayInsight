"""Analytics routes are mounted by :mod:`payinsight.api.app`."""
from payinsight.api.app import bank_performance, kpi_summary, method_performance, trends

__all__ = ["kpi_summary", "trends", "bank_performance", "method_performance"]
