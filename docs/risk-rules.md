# Risk rules

The engine emits evidence-backed findings for high value, failed transactions, shared
IP, shared device, customer velocity, and the Isolation Forest model anomaly. Points
are capped at 100: low `<25`, medium `25–49`, high `50–74`, critical `75+`.
Decisions are `allow`, `review`, and `block`. Rules are exposed through
`GET /api/risk/rules` so analysts can explain a decision without seeing ground-truth
labels.

