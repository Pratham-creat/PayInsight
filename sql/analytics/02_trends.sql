SELECT CAST(created_at AS DATE) AS date, COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr
FROM payments GROUP BY date ORDER BY date;
