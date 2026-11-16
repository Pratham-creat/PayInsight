SELECT payment_method, COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr
FROM payments GROUP BY payment_method;
