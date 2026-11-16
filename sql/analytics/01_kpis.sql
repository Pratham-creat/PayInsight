-- KPI summary for INR operations.
SELECT COUNT(*) AS transactions, SUM(amount_inr) AS volume_inr,
       AVG(CASE WHEN transaction_status = 'SUCCESS' THEN 1 ELSE 0 END) * 100 AS success_rate
FROM payments;
