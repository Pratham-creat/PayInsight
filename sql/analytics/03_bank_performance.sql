SELECT bank_name, COUNT(*) AS transactions,
       AVG(CASE WHEN transaction_status = 'SUCCESS' THEN 1 ELSE 0 END) * 100 AS success_rate
FROM payments GROUP BY bank_name;
