SELECT transaction_status, payment_method, COUNT(*) AS transactions
FROM payments GROUP BY transaction_status, payment_method;
