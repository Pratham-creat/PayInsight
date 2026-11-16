# Data dictionary

| Field | Type | Meaning |
|---|---|---|
| `transaction_id` | string | Stable `txn_` identifier |
| `merchant_id`, `customer_id` | string | Synthetic participant identifiers |
| `amount_inr` | decimal | Transaction value in Indian rupees |
| `payment_method` | enum | UPI, CARD, NET_BANKING, or WALLET |
| `bank_name` | enum | Indian acquiring/customer bank |
| `transaction_status` | enum | SUCCESS, FAILED, PENDING, or REFUNDED |
| `city`, `state` | string | Indian geography |
| `is_fraud`, `fraud_type` | internal | Generator ground truth; never returned by API |

