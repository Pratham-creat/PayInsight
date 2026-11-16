# PayInsight

PayInsight is a runnable payment-intelligence platform for fraud operations teams. It
generates deterministic payment events, validates and enriches them with Polars and
Pandera, stores analytical data in DuckDB, and combines explainable rules with a
scikit-learn Isolation Forest risk signal.

## Run locally

```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
payinsight-generate --count 1000
uvicorn payinsight.api.app:app --reload
```

Open `frontend/` with `npm install && npm run dev` in a second terminal. The API
provides `/api/metrics`, `/api/payments`, `/api/payments/{payment_id}/risk`, and
`/api/merchants/{merchant_id}/summary`.

```bash
make test
make lint
make frontend-build
```

## Product phases

1. **Generate:** deterministic, privacy-safe payments with intentional signal cases.
2. **Process:** typed Polars/Pandera contract, feature engineering, and DuckDB storage.
3. **Decide:** rule explanations plus unsupervised anomaly detection.
4. **Operate:** FastAPI metrics, payment search, merchant summaries, and a responsive dashboard.

See [architecture](docs/architecture.md) and [risk model](docs/risk-model.md).
