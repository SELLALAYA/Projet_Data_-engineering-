-- ============================================================
--   Price Intelligence Maroc — Initialisation PostgreSQL
--   Créé automatiquement au démarrage du container
-- ============================================================

-- Créer la base price_intelligence
SELECT 'CREATE DATABASE price_intelligence'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'price_intelligence')\gexec

\c price_intelligence;

-- ─────────────────────────────────────────
--  Table principale des produits
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id              SERIAL PRIMARY KEY,
    product_id      VARCHAR(255) UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    brand           VARCHAR(100),
    category        VARCHAR(100),
    source          VARCHAR(50),
    price           NUMERIC(12, 2),
    rating          NUMERIC(3, 2),
    url             TEXT,
    image_url       TEXT,
    scraped_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
--  Table historique des prix (time-series)
--  Simule Bigtable row key: product_id#timestamp
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS price_history (
    id              SERIAL PRIMARY KEY,
    product_id      VARCHAR(255) NOT NULL,
    price           NUMERIC(12, 2) NOT NULL,
    source          VARCHAR(50),
    recorded_at     TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ─────────────────────────────────────────
--  Table alertes prix (NiFi → PostgreSQL)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS price_alerts (
    id              SERIAL PRIMARY KEY,
    product_id      VARCHAR(255) NOT NULL,
    old_price       NUMERIC(12, 2),
    new_price       NUMERIC(12, 2),
    change_pct      NUMERIC(6, 2),
    alert_type      VARCHAR(50),  -- 'drop', 'spike'
    triggered_at    TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
--  Table quality report (Great Expectations)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS quality_reports (
    id              SERIAL PRIMARY KEY,
    run_date        DATE DEFAULT CURRENT_DATE,
    total_products  INT,
    missing_prices  INT,
    outliers        INT,
    passed_checks   INT,
    failed_checks   INT,
    report_json     JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_source ON products(source);
CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_time ON price_history(recorded_at);
CREATE INDEX IF NOT EXISTS idx_alerts_product ON price_alerts(product_id);

-- Message confirmation
DO $$ BEGIN
  RAISE NOTICE '✅ Base price_intelligence initialisée avec succès!';
END $$;
