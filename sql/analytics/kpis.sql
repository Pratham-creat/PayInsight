SELECT merchant_id, COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr,
       AVG(amount_inr) AS average_amount_inr,
       COUNT(*) FILTER (WHERE transaction_status = 'FAILED') AS failed_transactions
FROM payments GROUP BY merchant_id ORDER BY volume_inr DESC;
