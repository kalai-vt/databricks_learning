-- =====================================================================
-- 03_create_table.sql
-- Purpose : CREATE TABLE (managed) statements for all six demo tables
-- =====================================================================

USE CATALOG retail_sales;
USE SCHEMA sales;

CREATE TABLE IF NOT EXISTS customers (
  customer_id   STRING      NOT NULL COMMENT 'Unique customer identifier',
  customer_name STRING      COMMENT 'Full name of the customer',
  email         STRING      COMMENT 'Customer email address',
  city          STRING,
  state         STRING,
  signup_date   DATE        COMMENT 'Date the customer registered',
  segment       STRING      COMMENT 'Consumer | Corporate | Home Office'
)
COMMENT 'Retail customer master data';

CREATE TABLE IF NOT EXISTS products (
  product_id   STRING NOT NULL COMMENT 'Unique product identifier',
  product_name STRING,
  category     STRING,
  brand        STRING,
  unit_price   DECIMAL(10,2) COMMENT 'Price in INR'
)
COMMENT 'Product catalog';

CREATE TABLE IF NOT EXISTS orders (
  order_id     STRING NOT NULL COMMENT 'Unique order identifier',
  customer_id  STRING COMMENT 'FK -> customers.customer_id',
  product_id   STRING COMMENT 'FK -> products.product_id',
  order_date   DATE,
  quantity     INT,
  order_status STRING COMMENT 'Delivered | Cancelled | Returned'
)
COMMENT 'Customer orders';

CREATE TABLE IF NOT EXISTS sales (
  sale_id   STRING NOT NULL COMMENT 'Unique sale/transaction identifier',
  order_id  STRING COMMENT 'FK -> orders.order_id',
  sale_date DATE,
  amount    DECIMAL(10,2) COMMENT 'Transaction amount in INR',
  region    STRING,
  channel   STRING COMMENT 'Online | In-Store'
)
COMMENT 'Sales fact table used for revenue reporting';

USE CATALOG retail_hr;
USE SCHEMA hr;

CREATE TABLE IF NOT EXISTS departments (
  department_id   STRING NOT NULL COMMENT 'Unique department identifier',
  department_name STRING,
  location         STRING,
  manager_name     STRING
)
COMMENT 'Company departments';

CREATE TABLE IF NOT EXISTS employees (
  employee_id   STRING NOT NULL COMMENT 'Unique employee identifier',
  employee_name STRING,
  department_id STRING COMMENT 'FK -> departments.department_id',
  job_title     STRING,
  hire_date     DATE,
  salary        DECIMAL(12,2) COMMENT 'Annual salary in INR (sensitive)',
  email         STRING
)
COMMENT 'Employee master data — contains sensitive PII';

SHOW TABLES IN retail_sales.sales;
SHOW TABLES IN retail_hr.hr;
