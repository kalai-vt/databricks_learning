-- =====================================================================
-- 02_create_schema.sql
-- Purpose : CREATE SCHEMA statements for each department catalog
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS retail_sales.sales
COMMENT 'Core sales data: customers, products, orders, sales facts';

CREATE SCHEMA IF NOT EXISTS retail_hr.hr
COMMENT 'Core HR data: employees, departments';

CREATE SCHEMA IF NOT EXISTS retail_finance.finance
COMMENT 'Finance data sourced from external cloud storage';

SHOW SCHEMAS IN retail_sales;
SHOW SCHEMAS IN retail_hr;
SHOW SCHEMAS IN retail_finance;

USE CATALOG retail_sales;
USE SCHEMA sales;
SELECT CURRENT_CATALOG(), CURRENT_SCHEMA();
