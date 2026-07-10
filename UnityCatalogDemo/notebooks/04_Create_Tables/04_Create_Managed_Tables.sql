-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 4 — Creating Managed Tables
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC A **Managed Table** is a table whose **data and metadata are both fully controlled by Unity
-- MAGIC Catalog**. When you `CREATE TABLE` without a `LOCATION` clause:
-- MAGIC - Unity Catalog picks the storage path automatically (under the catalog/schema's managed storage root).
-- MAGIC - The data files are stored in **Delta Lake** format by default.
-- MAGIC - `DROP TABLE` deletes **both** the metadata **and the underlying data files**.
-- MAGIC
-- MAGIC This is the recommended default for most tables — you get automatic optimization (Delta, Liquid
-- MAGIC Clustering, predictive optimization) and don't have to manage storage paths yourself.
-- MAGIC
-- MAGIC We'll create the Sales department tables now, and the HR tables right after.

-- COMMAND ----------

USE CATALOG retail_sales;
USE SCHEMA sales;

-- COMMAND ----------

CREATE TABLE IF NOT EXISTS customers (
  customer_id   STRING      NOT NULL COMMENT 'Unique customer identifier',
  customer_name STRING      COMMENT 'Full name of the customer',
  email         STRING      COMMENT 'Customer email address',
  city          STRING,
  state         STRING,
  signup_date   DATE        COMMENT 'Date the customer registered',
  segment       STRING      COMMENT 'Consumer | Corporate | Home Office'
)
COMMENT 'Retail customer master data'
TBLPROPERTIES ('quality' = 'silver');

-- COMMAND ----------

CREATE TABLE IF NOT EXISTS products (
  product_id   STRING NOT NULL COMMENT 'Unique product identifier',
  product_name STRING,
  category     STRING,
  brand        STRING,
  unit_price   DECIMAL(10,2) COMMENT 'Price in INR'
)
COMMENT 'Product catalog';

-- COMMAND ----------

CREATE TABLE IF NOT EXISTS orders (
  order_id     STRING NOT NULL COMMENT 'Unique order identifier',
  customer_id  STRING COMMENT 'FK -> customers.customer_id',
  product_id   STRING COMMENT 'FK -> products.product_id',
  order_date   DATE,
  quantity     INT,
  order_status STRING COMMENT 'Delivered | Cancelled | Returned'
)
COMMENT 'Customer orders';

-- COMMAND ----------

CREATE TABLE IF NOT EXISTS sales (
  sale_id   STRING NOT NULL COMMENT 'Unique sale/transaction identifier',
  order_id  STRING COMMENT 'FK -> orders.order_id',
  sale_date DATE,
  amount    DECIMAL(10,2) COMMENT 'Transaction amount in INR',
  region    STRING,
  channel   STRING COMMENT 'Online | In-Store'
)
COMMENT 'Sales fact table used for revenue reporting';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC Four `CREATE TABLE` statements succeed. Verify:

-- COMMAND ----------

SHOW TABLES IN retail_sales.sales;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | database | tableName | isTemporary |
-- MAGIC |---|---|---|
-- MAGIC | sales | customers | false |
-- MAGIC | sales | products | false |
-- MAGIC | sales | orders | false |
-- MAGIC | sales | sales | false |

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Now the HR department's tables, in the `retail_hr.hr` schema.

-- COMMAND ----------

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
COMMENT 'Employee master data — contains sensitive PII, restrict access via GRANT';

-- COMMAND ----------

DESCRIBE TABLE EXTENDED retail_sales.sales.customers;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output (abridged)
-- MAGIC | col_name | data_type |
-- MAGIC |---|---|
-- MAGIC | customer_id | string |
-- MAGIC | customer_name | string |
-- MAGIC | ... | ... |
-- MAGIC | Type | MANAGED |
-- MAGIC | Provider | delta |
-- MAGIC | Location | s3://retailcorp-uc-metastore-root/retail_sales/sales/customers |
-- MAGIC
-- MAGIC `Type = MANAGED` confirms Unity Catalog owns the data lifecycle for this table.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - No `LOCATION` clause anywhere → every table above is **Managed**.
-- MAGIC - Column-level `COMMENT`s power the **Catalog Explorer** documentation view and AI-assisted search —
-- MAGIC   worth doing even in a demo.
-- MAGIC - Notice `employees.salary` is flagged sensitive in the comment — we'll restrict it with `GRANT` /
-- MAGIC   column masking discussion in the security demo.
