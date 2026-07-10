-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 2 — Creating Catalogs
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC A **Catalog** is the first (top) level of Unity Catalog's three-level namespace:
-- MAGIC
-- MAGIC ```
-- MAGIC catalog.schema.table
-- MAGIC ```
-- MAGIC
-- MAGIC Think of a Catalog as **one department/business unit's dedicated database server**. In our retail
-- MAGIC company, each department gets its own catalog so that data — and access to it — is cleanly isolated:
-- MAGIC
-- MAGIC | Department | Catalog Name |
-- MAGIC |---|---|
-- MAGIC | Sales | `retail_sales` |
-- MAGIC | Human Resources | `retail_hr` |
-- MAGIC | Finance | `retail_finance` |
-- MAGIC
-- MAGIC Under the old Hive Metastore, this level didn't exist — the workspace itself was effectively the
-- MAGIC only boundary, so every department shared the same flat database namespace.

-- COMMAND ----------

-- Create one catalog per department
CREATE CATALOG IF NOT EXISTS retail_sales
COMMENT 'Sales department: customers, products, orders, sales facts';

CREATE CATALOG IF NOT EXISTS retail_hr
COMMENT 'HR department: employees, departments';

CREATE CATALOG IF NOT EXISTS retail_finance
COMMENT 'Finance department: revenue and ledger data (external tables)';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC Each `CREATE CATALOG` returns no rows (DDL success). Verify with:

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
-- MAGIC | retail_sales |
-- MAGIC | retail_hr |
-- MAGIC | retail_finance |

-- COMMAND ----------

DESCRIBE CATALOG EXTENDED retail_sales;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | info_name | info_value |
-- MAGIC |---|---|
-- MAGIC | Catalog Name | retail_sales |
-- MAGIC | Comment | Sales department: customers, products, orders, sales facts |
-- MAGIC | Owner | <your-user> |
-- MAGIC | Storage Root | s3://retailcorp-uc-metastore-root/retail_sales |
-- MAGIC
-- MAGIC Notice the **Storage Root** — Unity Catalog automatically provisioned a managed storage path for this
-- MAGIC catalog under the Metastore's root storage. We didn't have to specify a bucket path ourselves.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - "One catalog per department" is a common, simple governance pattern — not a hard rule. Larger orgs
-- MAGIC   also use catalogs to separate environments (`dev`, `staging`, `prod`).
-- MAGIC - Catalogs are the primary unit at which broad access control decisions are made (e.g. "Finance team
-- MAGIC   cannot see the HR catalog at all").
-- MAGIC - `IF NOT EXISTS` makes the script safely re-runnable during a live demo.
