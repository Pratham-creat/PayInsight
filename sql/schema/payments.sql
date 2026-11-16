CREATE TABLE IF NOT EXISTS payments (
  transaction_id VARCHAR PRIMARY KEY, merchant_id VARCHAR NOT NULL, customer_id VARCHAR NOT NULL,
  amount_inr DECIMAL(18,2) CHECK (amount_inr > 0), currency VARCHAR(3) DEFAULT 'INR',
  payment_method VARCHAR NOT NULL, bank_name VARCHAR NOT NULL, transaction_status VARCHAR NOT NULL,
  merchant_category VARCHAR NOT NULL, city VARCHAR NOT NULL, state VARCHAR NOT NULL,
  ip_address VARCHAR NOT NULL, device_id VARCHAR NOT NULL, created_at TIMESTAMPTZ NOT NULL
);
