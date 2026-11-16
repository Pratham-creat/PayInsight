CREATE TABLE IF NOT EXISTS payments (
  payment_id VARCHAR PRIMARY KEY,
  merchant_id VARCHAR NOT NULL,
  customer_id VARCHAR NOT NULL,
  amount DECIMAL(18, 2) NOT NULL CHECK (amount > 0),
  currency VARCHAR(3) NOT NULL,
  status VARCHAR NOT NULL,
  payment_method VARCHAR NOT NULL,
  merchant_category VARCHAR NOT NULL,
  country VARCHAR(2) NOT NULL,
  ip_address VARCHAR NOT NULL,
  device_id VARCHAR NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);
