-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 13 — Cleanup
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC Tear down everything created during the demo, in **reverse dependency order** (views before
-- MAGIC tables, tables before schemas, schemas before catalogs). `DROP CATALOG ... CASCADE` is a shortcut
-- MAGIC that removes a catalog and everything inside it in one statement — use with care, it is
-- MAGIC **irreversible** for Managed objects (their data files are deleted, not just the metadata).
-- MAGIC
-- MAGIC Run this notebook only at the **end** of the session, or when resetting the environment before a
-- MAGIC repeat demo.

-- COMMAND ----------

-- MAGIC %md ## 13.1 Drop views

-- COMMAND ----------

DROP VIEW IF EXISTS retail_sales.sales.sales_summary_view;
DROP VIEW IF EXISTS retail_hr.hr.employee_department_view;

-- COMMAND ----------

-- MAGIC %md ## 13.2 Drop tables (managed + external)

-- COMMAND ----------

DROP TABLE IF EXISTS retail_sales.sales.orders;
DROP TABLE IF EXISTS retail_sales.sales.sales;
DROP TABLE IF EXISTS retail_sales.sales.products;
DROP TABLE IF EXISTS retail_sales.sales.customers;

DROP TABLE IF EXISTS retail_hr.hr.employees;
DROP TABLE IF EXISTS retail_hr.hr.departments;

-- External table: drops metadata only, files in s3://retailcorp-finance-raw/ledger/ remain untouched
DROP TABLE IF EXISTS retail_finance.finance.finance_ledger;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC All `DROP TABLE` statements succeed silently. Confirm:

-- COMMAND ----------

SHOW TABLES IN retail_sales.sales;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC *(empty result set)*

-- COMMAND ----------

-- MAGIC %md ## 13.3 Drop the volume

-- COMMAND ----------

DROP VOLUME IF EXISTS retail_sales.sales.raw_files;

-- COMMAND ----------

-- MAGIC %md ## 13.4 Drop schemas

-- COMMAND ----------

DROP SCHEMA IF EXISTS retail_sales.sales CASCADE;
DROP SCHEMA IF EXISTS retail_hr.hr CASCADE;
DROP SCHEMA IF EXISTS retail_finance.finance CASCADE;

-- COMMAND ----------

-- MAGIC %md ## 13.5 Drop catalogs

-- COMMAND ----------

DROP CATALOG IF EXISTS retail_sales CASCADE;
DROP CATALOG IF EXISTS retail_hr CASCADE;
DROP CATALOG IF EXISTS retail_finance CASCADE;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output

-- COMMAND ----------

SHOW CATALOGS;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | catalog |
-- MAGIC |---|
-- MAGIC | main |
-- MAGIC | system |
-- MAGIC | samples |
-- MAGIC | hive_metastore |
-- MAGIC
-- MAGIC Back to the original state — `retail_sales`, `retail_hr`, `retail_finance` are gone.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 13.6 (Optional) Clean up demo grants on principals
-- MAGIC If the demo users/groups are not reused elsewhere, an admin may also want to drop them via the
-- MAGIC Account Console — grants tied to a deleted catalog are removed automatically, so this step is
-- MAGIC optional and not required for a clean re-run.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - `CASCADE` is the Unity Catalog equivalent of `DROP DATABASE ... CASCADE` — powerful, destructive,
-- MAGIC   and exactly why `DROP CATALOG`/`DROP SCHEMA` privileges are tightly restricted in production.
-- MAGIC - Dropping the external table never touched the Finance department's S3 files — a good moment to
-- MAGIC   reinforce the Managed vs. External distinction one more time before wrapping up.
