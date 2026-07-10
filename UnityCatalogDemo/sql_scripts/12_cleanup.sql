-- =====================================================================
-- 12_cleanup.sql
-- Purpose : Full teardown, reverse dependency order (mirrors
--           notebooks/13_Cleanup/13_Cleanup.sql)
-- =====================================================================

DROP VIEW IF EXISTS retail_sales.sales.sales_summary_view;
DROP VIEW IF EXISTS retail_hr.hr.employee_department_view;

DROP TABLE IF EXISTS retail_sales.sales.orders;
DROP TABLE IF EXISTS retail_sales.sales.sales;
DROP TABLE IF EXISTS retail_sales.sales.products;
DROP TABLE IF EXISTS retail_sales.sales.customers;
DROP TABLE IF EXISTS retail_hr.hr.employees;
DROP TABLE IF EXISTS retail_hr.hr.departments;
DROP TABLE IF EXISTS retail_finance.finance.finance_ledger; -- metadata only, files untouched

DROP VOLUME IF EXISTS retail_sales.sales.raw_files;

DROP SCHEMA IF EXISTS retail_sales.sales CASCADE;
DROP SCHEMA IF EXISTS retail_hr.hr CASCADE;
DROP SCHEMA IF EXISTS retail_finance.finance CASCADE;

DROP CATALOG IF EXISTS retail_sales CASCADE;
DROP CATALOG IF EXISTS retail_hr CASCADE;
DROP CATALOG IF EXISTS retail_finance CASCADE;

SHOW CATALOGS; -- confirm retail_sales / retail_hr / retail_finance are gone
