-- =====================================================================
-- 09_alter_drop.sql
-- Purpose : ALTER and DROP examples across every object type
-- =====================================================================

-- ALTER ------------------------------------------------------------
ALTER CATALOG retail_sales SET OWNER TO `admin_user@retailcorp.com`;
ALTER CATALOG retail_sales SET TAGS ('department' = 'sales', 'environment' = 'demo');

ALTER SCHEMA retail_sales.sales SET TAGS ('pii' = 'false');

ALTER TABLE retail_sales.sales.customers ADD COLUMN loyalty_tier STRING COMMENT 'Bronze | Silver | Gold';
ALTER TABLE retail_sales.sales.customers ALTER COLUMN loyalty_tier COMMENT 'Loyalty program tier';
ALTER TABLE retail_sales.sales.customers RENAME COLUMN loyalty_tier TO membership_tier;
ALTER TABLE retail_sales.sales.customers DROP COLUMN membership_tier;

ALTER TABLE retail_sales.sales.orders SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true');

ALTER VIEW retail_sales.sales.sales_summary_view SET TBLPROPERTIES ('comment' = 'Revenue view for Power BI');

-- DROP ---------------------------------------------------------------
-- (destructive — shown here for reference; full teardown lives in
--  notebooks/13_Cleanup and sql_scripts/13_cleanup.sql)
-- DROP VIEW IF EXISTS retail_sales.sales.sales_summary_view;
-- DROP TABLE IF EXISTS retail_sales.sales.orders;
-- DROP SCHEMA IF EXISTS retail_sales.sales CASCADE;
-- DROP CATALOG IF EXISTS retail_sales CASCADE;
