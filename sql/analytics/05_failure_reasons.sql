SELECT failure_reason, COUNT(*) AS failures FROM payments
WHERE transaction_status = 'FAILED' GROUP BY failure_reason;
