CREATE TABLE IF NOT EXISTS payroll_events (
    employee_id VARCHAR, employer_id VARCHAR, pay_date DATE,
    gross_pay DECIMAL(18,2), net_pay DECIMAL(18,2), hours DECIMAL(10,2),
    bank_account_hash VARCHAR, created_at TIMESTAMP
);
