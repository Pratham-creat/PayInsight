# Architecture

`generator` emits Pydantic `PaymentEvent` objects in bounded chunks. `pipeline` converts
them into Polars frames, validates the contract with Pandera, and adds model-ready
features without mutating source events. `warehouse` provides a small DuckDB repository
for local development and repeatable analytics.

The API constructs a demo resource once per process. Production deployments should
replace `build_demo` with an ingestion job and a persistent DuckDB/Parquet location.
The frontend talks only to the API and has no access to payment secrets.

All generated identifiers are deterministic hashes rather than real customer data.
