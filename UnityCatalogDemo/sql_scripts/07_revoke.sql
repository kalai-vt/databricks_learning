-- =====================================================================
-- 07_revoke.sql
-- Purpose : REVOKE statements — demonstrate removing privileges
-- =====================================================================

-- Remove one table-level privilege
REVOKE SELECT ON TABLE retail_sales.sales.products FROM `sales_user@retailcorp.com`;
SHOW GRANTS `sales_user@retailcorp.com` ON TABLE retail_sales.sales.products; -- expect: empty

-- Restore it
GRANT SELECT ON TABLE retail_sales.sales.products TO `sales_user@retailcorp.com`;

-- Full catalog lock-out example
REVOKE USE CATALOG ON CATALOG retail_finance FROM `finance_user@retailcorp.com`;
-- Any query finance_user@retailcorp.com runs against retail_finance.* now fails with
-- [INSUFFICIENT_PERMISSIONS] even though table-level SELECT grants still technically exist.

-- Restore access for the rest of the demo
GRANT USE CATALOG ON CATALOG retail_finance TO `finance_user@retailcorp.com`;

-- Revoke ALL PRIVILEGES example (used during cleanup / offboarding a principal)
-- REVOKE ALL PRIVILEGES ON CATALOG retail_hr FROM `hr_user@retailcorp.com`;
