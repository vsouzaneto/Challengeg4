CREATE TABLE accounts (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  sector TEXT,
  year_established INTEGER CHECK (year_established IS NULL OR year_established > 0),
  revenue NUMERIC(14, 2) CHECK (revenue IS NULL OR revenue >= 0),
  employees INTEGER CHECK (employees IS NULL OR employees > 0),
  office_location TEXT,
  subsidiary_id BIGINT REFERENCES accounts(id) ON DELETE SET NULL
);

CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  series TEXT,
  sales_price NUMERIC(14, 2) CHECK (sales_price IS NULL OR sales_price >= 0)
);

CREATE TABLE sales_agents (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  manager TEXT,
  regional_office TEXT
);

CREATE TABLE opportunities (
  id TEXT PRIMARY KEY,
  sales_agent_id BIGINT NOT NULL REFERENCES sales_agents(id),
  product_id BIGINT NOT NULL REFERENCES products(id),
  account_id BIGINT REFERENCES accounts(id) ON DELETE SET NULL,
  deal_stage TEXT NOT NULL CHECK (deal_stage IN ('Prospecting', 'Engaging', 'Won', 'Lost')),
  engage_date DATE,
  close_date DATE,
  close_value NUMERIC(14, 2) CHECK (close_value IS NULL OR close_value >= 0),
  CHECK (
    (deal_stage IN ('Won', 'Lost') AND close_date IS NOT NULL)
    OR (deal_stage IN ('Prospecting', 'Engaging') AND close_date IS NULL)
  )
);

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sessions (
  token_hash CHAR(64) PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX accounts_sector_idx ON accounts(sector);
CREATE INDEX opportunities_account_idx ON opportunities(account_id);
CREATE INDEX opportunities_product_idx ON opportunities(product_id);
CREATE INDEX opportunities_agent_idx ON opportunities(sales_agent_id);
CREATE INDEX opportunities_stage_idx ON opportunities(deal_stage);
CREATE INDEX opportunities_close_date_idx ON opportunities(close_date);
CREATE INDEX opportunities_history_idx ON opportunities(deal_stage, close_date) WHERE deal_stage IN ('Won', 'Lost');
CREATE INDEX sessions_user_idx ON sessions(user_id);
CREATE INDEX sessions_expiry_idx ON sessions(expires_at);
