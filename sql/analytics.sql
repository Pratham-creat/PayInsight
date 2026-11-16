SELECT employee_id, COUNT(*) AS events, SUM(gross_pay) AS gross_total,
       SUM(net_pay) AS net_total
FROM payroll_events GROUP BY employee_id ORDER BY gross_total DESC;
