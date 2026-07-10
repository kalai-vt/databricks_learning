-- =====================================================================
-- 01_create_catalog.sql
-- Purpose : CREATE CATALOG statements for the RetailCorp UC demo
-- Run as  : Metastore admin or a principal with CREATE CATALOG privilege
-- =====================================================================

CREATE CATALOG IF NOT EXISTS retail_sales
COMMENT 'Sales department: customers, products, orders, sales facts';

CREATE CATALOG IF NOT EXISTS retail_hr
COMMENT 'HR department: employees, departments';

CREATE CATALOG IF NOT EXISTS retail_finance
COMMENT 'Finance department: revenue and ledger data (external tables)';

-- Optional: pin a catalog to a specific managed storage location instead of
-- inheriting the Metastore's default root (uncomment and adjust the path):
-- CREATE CATALOG IF NOT EXISTS retail_sales
-- MANAGED LOCATION 's3://retailcorp-uc-metastore-root/retail_sales'
-- COMMENT 'Sales department catalog with a dedicated storage root';

SHOW CATALOGS;
