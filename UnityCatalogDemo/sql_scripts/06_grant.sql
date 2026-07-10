-- =====================================================================
-- 06_grant.sql
-- Purpose : GRANT statements implementing RBAC for the demo principals
-- Principals:
--   admin_user@retailcorp.com    - full access, all catalogs
--   sales_user@retailcorp.com    - retail_sales only
--   hr_user@retailcorp.com       - retail_hr only
--   finance_user@retailcorp.com  - retail_finance + read-only sales view
-- =====================================================================

-- Sales team
GRANT USE CATALOG ON CATALOG retail_sales TO `sales_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_sales.sales TO `sales_user@retailcorp.com`;
GRANT SELECT ON TABLE retail_sales.sales.customers TO `sales_user@retailcorp.com`;
GRANT SELECT ON TABLE retail_sales.sales.products  TO `sales_user@retailcorp.com`;
GRANT SELECT, MODIFY ON TABLE retail_sales.sales.orders TO `sales_user@retailcorp.com`;
GRANT SELECT, MODIFY ON TABLE retail_sales.sales.sales  TO `sales_user@retailcorp.com`;
GRANT SELECT ON VIEW retail_sales.sales.sales_summary_view TO `sales_user@retailcorp.com`;

-- HR team
GRANT USE CATALOG ON CATALOG retail_hr TO `hr_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_hr.hr TO `hr_user@retailcorp.com`;
GRANT ALL PRIVILEGES ON SCHEMA retail_hr.hr TO `hr_user@retailcorp.com`;

-- Finance team
GRANT USE CATALOG ON CATALOG retail_finance TO `finance_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_finance.finance TO `finance_user@retailcorp.com`;
GRANT SELECT ON SCHEMA retail_finance.finance TO `finance_user@retailcorp.com`;
GRANT USE CATALOG ON CATALOG retail_sales TO `finance_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_sales.sales TO `finance_user@retailcorp.com`;
GRANT SELECT ON VIEW retail_sales.sales.sales_summary_view TO `finance_user@retailcorp.com`;

-- Admin
GRANT ALL PRIVILEGES ON CATALOG retail_sales   TO `admin_user@retailcorp.com`;
GRANT ALL PRIVILEGES ON CATALOG retail_hr      TO `admin_user@retailcorp.com`;
GRANT ALL PRIVILEGES ON CATALOG retail_finance TO `admin_user@retailcorp.com`;

-- Verification
SHOW GRANTS ON CATALOG retail_sales;
SHOW GRANTS ON CATALOG retail_hr;
SHOW GRANTS ON CATALOG retail_finance;
SHOW GRANTS `sales_user@retailcorp.com` ON TABLE retail_sales.sales.orders;
