# Validation report

The full pipeline validates required non-null columns, unique transaction identifiers,
positive INR amounts, INR currency, supported Indian payment methods/banks/statuses,
and UTC timestamps using Pandera's Polars backend. `GET /api/validation-report` returns
the checks executed by the demo service. Evaluation labels remain in the warehouse
fixture for offline recall/precision analysis and are intentionally excluded from all
public API projections.
