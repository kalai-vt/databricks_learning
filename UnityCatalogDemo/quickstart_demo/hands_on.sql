-- =====================================================================
-- QUICKSTART: Unity Catalog in ~20 minutes, hands-on
-- Run every statement top-to-bottom, in order, in a Databricks SQL
-- editor or notebook. Minimal data, minimal setup, every core concept.
-- =====================================================================


-- ── STEP 1: Confirm Unity Catalog is active ──────────────────────────
-- A Metastore is the top-level container for everything we're about to
-- create. You don't create it here (an admin does that once); we just
-- confirm we're connected to one.
SELECT CURRENT_METASTORE();
SHOW CATALOGS;                 -- you'll see main, system, samples, hive_metastore


-- ── STEP 2: Create a Catalog ──────────────────────────────────────────
-- A Catalog is the top level of the name "catalog.schema.table".
-- Think of it as one company/department's own database server.
CREATE CATALOG IF NOT EXISTS uc_quickstart
COMMENT 'Quickstart demo catalog';

SHOW CATALOGS;                 -- uc_quickstart now appears


-- ── STEP 3: Create a Schema ───────────────────────────────────────────
-- A Schema is a folder inside the catalog, grouping related tables.
CREATE SCHEMA IF NOT EXISTS uc_quickstart.retail
COMMENT 'Retail data for the quickstart';

USE CATALOG uc_quickstart;
USE SCHEMA retail;
SELECT CURRENT_CATALOG(), CURRENT_SCHEMA();


-- ── STEP 4: Create a Managed Table + load 5 rows ─────────────────────
-- No LOCATION clause = MANAGED table. Unity Catalog owns the storage
-- path and the data lifecycle automatically.
CREATE TABLE IF NOT EXISTS products (
  product_id   STRING,
  product_name STRING,
  category     STRING,
  price        DECIMAL(10,2)
)
COMMENT 'Simple product list';

INSERT INTO products VALUES
('P1','Wireless Mouse','Electronics',799.00),
('P2','Yoga Mat','Fitness',999.00),
('P3','Cotton T-Shirt','Apparel',599.00),
('P4','LED Desk Lamp','Home',1299.00),
('P5','Running Shoes','Footwear',3299.00);

SELECT * FROM products;

CREATE TABLE IF NOT EXISTS orders (
  order_id      STRING,
  product_id    STRING,
  customer_name STRING,
  quantity      INT
)
COMMENT 'Simple orders list';

INSERT INTO orders VALUES
('O1','P1','Aarav',2),
('O2','P2','Priya',1),
('O3','P3','Rohan',3),
('O4','P4','Sneha',1),
('O5','P5','Karan',1);

SELECT * FROM orders;

-- Prove it's Managed:
DESCRIBE TABLE EXTENDED products;   -- look for Type = MANAGED


-- ── STEP 5: Create a View ─────────────────────────────────────────────
-- A View stores no data — just a saved query, joined live every time.
CREATE OR REPLACE VIEW order_summary_view AS
SELECT o.order_id, o.customer_name, p.product_name, p.category,
       o.quantity, (o.quantity * p.price) AS total_amount
FROM orders o
JOIN products p ON o.product_id = p.product_id;

SELECT * FROM order_summary_view;


-- ── STEP 6: Create a Volume ───────────────────────────────────────────
-- A Volume governs access to raw FILES (not tables) — CSVs, images, etc.
-- Same GRANT/REVOKE model as tables, just for files.
CREATE VOLUME IF NOT EXISTS raw_files
COMMENT 'Landing zone for raw files';

SHOW VOLUMES IN uc_quickstart.retail;
-- File path you could upload to: /Volumes/uc_quickstart/retail/raw_files/


-- ── STEP 7: External Table (concept only — needs real cloud storage) ──
-- A Managed Table = Unity Catalog owns the files (DROP deletes data too).
-- An External Table = you point at an existing cloud path; DROP only
-- removes the metadata, the files stay put. Same CREATE TABLE syntax,
-- just add a LOCATION clause:
--
-- CREATE TABLE finance_ledger (...)
-- LOCATION 's3://your-bucket/some/existing/path/';
--
-- (Skipped here — requires a real Storage Credential + External
-- Location set up by an admin. See sql_scripts/11_external_table_volume.sql
-- in the main demo for the full pattern.)


-- ── STEP 8: Grant & Revoke (RBAC) ─────────────────────────────────────
-- Replace the email below with a real second user in your workspace to
-- see this fully (or your own email, to confirm the syntax works).
GRANT USE CATALOG ON CATALOG uc_quickstart TO `REPLACE_WITH_A_USER_EMAIL`;
GRANT USE SCHEMA  ON SCHEMA  uc_quickstart.retail TO `REPLACE_WITH_A_USER_EMAIL`;
GRANT SELECT ON TABLE uc_quickstart.retail.products TO `REPLACE_WITH_A_USER_EMAIL`;

SHOW GRANTS ON TABLE uc_quickstart.retail.products;

-- Now try this AS that other user (if you have a second login):
--   SELECT * FROM uc_quickstart.retail.orders;   -- fails: no grant on orders
--   SELECT * FROM uc_quickstart.retail.products;  -- works: SELECT was granted

REVOKE SELECT ON TABLE uc_quickstart.retail.products FROM `REPLACE_WITH_A_USER_EMAIL`;
SHOW GRANTS ON TABLE uc_quickstart.retail.products;   -- grant is gone


-- ── STEP 9: Lineage ────────────────────────────────────────────────────
-- Nothing to run — this is captured automatically. Go to:
--   Catalog Explorer -> uc_quickstart -> retail -> order_summary_view -> Lineage tab
-- You'll see "products" and "orders" as upstream tables, tracked with
-- zero extra configuration, because we created the view from them in Step 5.


-- ── STEP 10: Cleanup ───────────────────────────────────────────────────
-- Run this when you're done, to reset the workspace.
-- DROP VIEW IF EXISTS uc_quickstart.retail.order_summary_view;
-- DROP VOLUME IF EXISTS uc_quickstart.retail.raw_files;
-- DROP TABLE IF EXISTS uc_quickstart.retail.products;
-- DROP TABLE IF EXISTS uc_quickstart.retail.orders;
-- DROP SCHEMA IF EXISTS uc_quickstart.retail CASCADE;
-- DROP CATALOG IF EXISTS uc_quickstart CASCADE;
