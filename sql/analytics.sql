-- Merchant operating view used by dashboards and investigations.
SELECT merchant_id, COUNT(*) AS payments, SUM(amount) AS volume,
       AVG(amount) AS average_amount,
       COUNT(*) FILTER (WHERE status = 'failed') AS failed_payments
FROM payments
GROUP BY merchant_id
ORDER BY volume DESC;

-- Customer velocity view used by the risk engine.
SELECT customer_id, COUNT(*) AS payment_count, SUM(amount) AS volume,
       COUNT(DISTINCT ip_address) AS unique_ips,
       COUNT(DISTINCT device_id) AS unique_devices
FROM payments
GROUP BY customer_id;
