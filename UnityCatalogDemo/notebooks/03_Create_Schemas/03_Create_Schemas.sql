-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 3 — Creating Schemas
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC A **Schema** (also called a *database*) is the second level of the three-level namespace:
-- MAGIC `catalog.schema.table`. A Schema groups related tables, views, and volumes together —
-- MAGIC think of it as a **folder inside the catalog**.
-- MAGIC
-- MAGIC We will create one primary schema per catalog to keep the demo simple:
-- MAGIC
-- MAGIC | Catalog | Schema | Purpose |
-- MAGIC |---|---|---|
-- MAGIC | `retail_sales` | `sales` | customers, products, orders, sales facts, views, volumes |
-- MAGIC | `retail_hr` | `hr` | employees, departments |
-- MAGIC | `retail_finance` | `finance` | external finance ledger table |
-- MAGIC
-- MAGIC In a bigger real project you might add more schemas, e.g. `retail_sales.staging` for raw landing
-- MAGIC data and `retail_sales.curated` for cleaned data — schemas are cheap to create.

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS retail_sales.sales
COMMENT 'Core sales data: customers, products, orders, sales facts';

CREATE SCHEMA IF NOT EXISTS retail_hr.hr
COMMENT 'Core HR data: employees, departments';

CREATE SCHEMA IF NOT EXISTS retail_finance.finance
COMMENT 'Finance data sourced from external cloud storage';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC Three DDL statements succeed silently. Verify with `SHOW SCHEMAS`:

-- COMMAND ----------

SHOW SCHEMAS IN retail_sales;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | databaseName |
-- MAGIC |---|
-- MAGIC | default |
-- MAGIC | information_schema |
-- MAGIC | sales |
-- MAGIC
-- MAGIC `default` and `information_schema` are created automatically with every catalog.
-- MAGIC `information_schema` is a special read-only schema exposing metadata (columns, tables, privileges)
-- MAGIC — the Unity Catalog equivalent of ANSI SQL's `INFORMATION_SCHEMA`.

-- COMMAND ----------

-- Switch context so we don't have to fully qualify every object name for the rest of the demo
USE CATALOG retail_sales;
USE SCHEMA sales;

SELECT CURRENT_CATALOG(), CURRENT_SCHEMA();

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | current_catalog() | current_schema() |
-- MAGIC |---|---|
-- MAGIC | retail_sales | sales |

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - `USE CATALOG` + `USE SCHEMA` set your session context, similar to `USE DATABASE` in traditional SQL
-- MAGIC   engines — but now there's an extra level.
-- MAGIC - Fully-qualified three-level names (`retail_sales.sales.customers`) always work regardless of
-- MAGIC   session context — good practice in production notebooks and BI tool connections.
