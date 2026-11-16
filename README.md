# PayInsight

PayInsight is a small, runnable payroll-risk analytics MVP. It generates deterministic
payroll events in chunks, transforms them through a typed pipeline, stores the result in
DuckDB, and exposes rule-based risk scoring through a FastAPI service.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
make test
uvicorn payinsight.api.app:app --reload
```

`GET /health`, `GET /metrics`, and `GET /employees/{employee_id}/risk` are available.
The default generator is deterministic (`seed=42`) and never requires production data.

See `docs/architecture.md` and `docs/risk-model.md` for design notes.