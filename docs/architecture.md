# Architecture

`generator` emits deterministic Pydantic events in bounded chunks. `pipeline` validates,
normalises, enriches, and aggregates. `risk` applies explainable rules. `warehouse` provides
a small DuckDB persistence boundary, while `api` serves health, metrics, and employee risk.
All components are importable independently for batch jobs or a web process.
