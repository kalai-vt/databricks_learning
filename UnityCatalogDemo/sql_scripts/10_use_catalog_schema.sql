-- =====================================================================
-- 10_use_catalog_schema.sql
-- Purpose : USE CATALOG / USE SCHEMA session-context examples
-- =====================================================================

-- Set session context so subsequent statements can use short (unqualified) names
USE CATALOG retail_sales;
USE SCHEMA sales;
SELECT CURRENT_CATALOG(), CURRENT_SCHEMA();
SELECT * FROM customers LIMIT 5;              -- resolves to retail_sales.sales.customers

USE CATALOG retail_hr;
USE SCHEMA hr;
SELECT CURRENT_CATALOG(), CURRENT_SCHEMA();
SELECT * FROM employees LIMIT 5;              -- resolves to retail_hr.hr.employees

-- Fully-qualified names always work regardless of session context,
-- and are the recommended style for production notebooks/BI connections:
SELECT * FROM retail_finance.finance.finance_ledger LIMIT 5;

-- Reset to a neutral default at the end of a script
USE CATALOG main;
