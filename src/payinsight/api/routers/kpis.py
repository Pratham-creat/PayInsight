"""Compatibility exports for KPI routes mounted by the application."""

from payinsight.api.app import kpi_summary, trends

__all__ = ["kpi_summary", "trends"]
