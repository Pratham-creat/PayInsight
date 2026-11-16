# Risk model

Every payment receives a score from 0–100 and an explanation. The score is the capped
sum of these signals:

| Signal | Points | Meaning |
| --- | ---: | --- |
| High amount | 30 | More than 3× the merchant average and above $500 |
| Failed payment | 15 | The payment was declined |
| IP reuse | 25 | One IP is associated with at least three customers |
| Device reuse | 40 | One device is associated with at least three customers |
| Velocity | 25 | A customer has at least eight observed payments |
| Model anomaly | 20 | Isolation Forest marks amount/velocity as unusual |

Bands are low (<25), medium (25–49), high (50–74), and critical (75+). Decisions
are `allow`, `review` (40+), or `block` (75+). Findings include evidence fields so an
analyst can understand and reproduce every decision.
