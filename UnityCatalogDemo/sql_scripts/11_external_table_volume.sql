-- =====================================================================
-- 11_external_table_volume.sql
-- Purpose : Storage Credential / External Location / External Table /
--           Volume examples
-- =====================================================================

-- Admin-only setup (reference — requires cloud IAM trust) --------------
-- CREATE STORAGE CREDENTIAL IF NOT EXISTS finance_storage_credential
-- WITH ( AWS_IAM_ROLE 'arn:aws:iam::<account-id>:role/unity-catalog-finance-role' )
-- COMMENT 'Assumed by Unity Catalog to access the Finance raw storage bucket';

-- CREATE EXTERNAL LOCATION IF NOT EXISTS finance_raw_location
-- URL 's3://retailcorp-finance-raw/ledger/'
-- WITH (STORAGE CREDENTIAL finance_storage_credential)
-- COMMENT 'Finance ledger extracts landed by the upstream SAP export job';

SHOW STORAGE CREDENTIALS;
SHOW EXTERNAL LOCATIONS;

-- External Table ---------------------------------------------------
USE CATALOG retail_finance;
USE SCHEMA finance;

CREATE TABLE IF NOT EXISTS finance_ledger (
  sale_id   STRING,
  order_id  STRING,
  sale_date DATE,
  amount    DECIMAL(10,2),
  region    STRING,
  channel   STRING
)
COMMENT 'External table: data physically owned by the Finance department bucket'
LOCATION 's3://retailcorp-finance-raw/ledger/';

DESCRIBE TABLE EXTENDED retail_finance.finance.finance_ledger;  -- Type = EXTERNAL

-- Managed Volume -----------------------------------------------------
USE CATALOG retail_sales;
USE SCHEMA sales;

CREATE VOLUME IF NOT EXISTS raw_files
COMMENT 'Landing zone for raw CSV files before they are loaded into managed Delta tables';

SHOW VOLUMES IN retail_sales.sales;
DESCRIBE VOLUME retail_sales.sales.raw_files;

-- Read files directly from the Volume with SQL
-- SELECT * FROM read_files('/Volumes/retail_sales/sales/raw_files/customers.csv',
--                          format => 'csv', header => true);

-- Production load pattern: COPY INTO from a Volume into a managed Delta table
-- COPY INTO retail_sales.sales.customers
-- FROM '/Volumes/retail_sales/sales/raw_files/customers.csv'
-- FILEFORMAT = CSV
-- FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true')
-- COPY_OPTIONS ('mergeSchema' = 'true');

-- External Volume example (points at an existing External Location path)
-- CREATE EXTERNAL VOLUME IF NOT EXISTS retail_finance.finance.finance_docs
-- LOCATION 's3://retailcorp-finance-raw/documents/'
-- COMMENT 'Scanned invoices and supporting documents';
