-- =====================================================================
-- 03_access_denied_demo.sql
-- Purpose : Run each block AS the named user (switch identity/browser
--           profile per persona) to see Unity Catalog RBAC enforced live.
-- =====================================================================

-- ---------------------------------------------------------------------
-- AS sales_user@retailcorp.com
-- ---------------------------------------------------------------------
SELECT * FROM retail_sales.sales.customers LIMIT 5;
-- Expected: SUCCESS - sales_user has SELECT on this table

SELECT * FROM retail_hr.hr.employees LIMIT 5;
-- Expected: FAILURE
-- Error: [INSUFFICIENT_PERMISSIONS] PERMISSION_DENIED: User does not have
-- USE CATALOG on Catalog 'retail_hr'.

INSERT INTO retail_sales.sales.customers VALUES
  ('C999','Test Hacker','test@example.com','Nowhere','NA',DATE'2024-01-01','Consumer');
-- Expected: FAILURE
-- Error: [INSUFFICIENT_PERMISSIONS] User does not have MODIFY on Table
-- 'retail_sales.sales.customers'. (sales_user only has SELECT on customers)

-- ---------------------------------------------------------------------
-- AS hr_user@retailcorp.com
-- ---------------------------------------------------------------------
SELECT * FROM retail_hr.hr.employees LIMIT 5;
-- Expected: SUCCESS - hr_user has ALL PRIVILEGES on schema retail_hr.hr

SELECT * FROM retail_sales.sales.orders LIMIT 5;
-- Expected: FAILURE
-- Error: [INSUFFICIENT_PERMISSIONS] User does not have USE CATALOG on
-- Catalog 'retail_sales'.

-- ---------------------------------------------------------------------
-- AS finance_user@retailcorp.com
-- ---------------------------------------------------------------------
SELECT * FROM retail_sales.sales.sales_summary_view LIMIT 5;
-- Expected: SUCCESS - finance_user has SELECT on the view

SELECT * FROM retail_sales.sales.orders LIMIT 5;
-- Expected: FAILURE (view access does NOT imply base-table access)
-- Error: [INSUFFICIENT_PERMISSIONS] User does not have SELECT on Table
-- 'retail_sales.sales.orders'.

SELECT * FROM retail_hr.hr.employees LIMIT 5;
-- Expected: FAILURE
-- Error: [INSUFFICIENT_PERMISSIONS] User does not have USE CATALOG on
-- Catalog 'retail_hr'.

-- ---------------------------------------------------------------------
-- AS admin_user@retailcorp.com
-- ---------------------------------------------------------------------
SELECT * FROM retail_sales.sales.customers LIMIT 5;   -- SUCCESS
SELECT * FROM retail_hr.hr.employees LIMIT 5;          -- SUCCESS
SELECT * FROM retail_finance.finance.finance_ledger LIMIT 5; -- SUCCESS
-- Admin has ALL PRIVILEGES on every catalog created in this demo.
