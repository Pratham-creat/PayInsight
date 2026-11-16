SELECT customer_id, COUNT(*) AS transaction_count, SUM(amount_inr) AS volume_inr
FROM payments GROUP BY customer_id;
