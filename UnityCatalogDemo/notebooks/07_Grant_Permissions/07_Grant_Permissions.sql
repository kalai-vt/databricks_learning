-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 7 — Granting Permissions (RBAC in Unity Catalog)
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC Unity Catalog uses standard SQL **GRANT** statements for access control — this is its
-- MAGIC **Role-Based / attribute-based Access Control (RBAC)** model, enforced centrally for every
-- MAGIC workspace attached to the Metastore (unlike Hive Metastore, where permissions were often
-- MAGIC inconsistent per cluster/workspace or not enforced at all).
-- MAGIC
-- MAGIC Privileges cascade down the hierarchy: `Metastore → Catalog → Schema → Table/View/Volume`.
-- MAGIC To query a table, a principal needs:
-- MAGIC 1. `USE CATALOG` on the catalog, **and**
-- MAGIC 2. `USE SCHEMA` on the schema, **and**
-- MAGIC 3. `SELECT` on the table (or `ALL PRIVILEGES`, which includes it).
-- MAGIC
-- MAGIC Missing any one of the three results in **Access Denied** — this is the "layered lock" model,
-- MAGIC and it's exactly what we'll demonstrate live in the Security Demo.
-- MAGIC
-- MAGIC ### Our demo principals
-- MAGIC | Principal | Role |
-- MAGIC |---|---|
-- MAGIC | `admin_user@retailcorp.com` | Metastore Admin — full access everywhere |
-- MAGIC | `sales_user@retailcorp.com` | Sales department — read/write on `retail_sales` only |
-- MAGIC | `hr_user@retailcorp.com` | HR department — read/write on `retail_hr` only |
-- MAGIC | `finance_user@retailcorp.com` | Finance department — read on `retail_finance` + read-only on the sales summary view for revenue reporting |
-- MAGIC
-- MAGIC (In a real workspace these would be account-level users/groups synced from your identity provider.
-- MAGIC Replace the emails below with real principals in your workspace before running.)

-- COMMAND ----------

-- MAGIC %md ## 7.1 Grant SALES team access to the Sales catalog

-- COMMAND ----------

GRANT USE CATALOG ON CATALOG retail_sales TO `sales_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_sales.sales TO `sales_user@retailcorp.com`;

-- SELECT: read-only
GRANT SELECT ON TABLE retail_sales.sales.customers TO `sales_user@retailcorp.com`;
GRANT SELECT ON TABLE retail_sales.sales.products  TO `sales_user@retailcorp.com`;

-- MODIFY: read + write (INSERT/UPDATE/DELETE), needed because Sales owns order entry
GRANT SELECT, MODIFY ON TABLE retail_sales.sales.orders TO `sales_user@retailcorp.com`;
GRANT SELECT, MODIFY ON TABLE retail_sales.sales.sales  TO `sales_user@retailcorp.com`;

GRANT SELECT ON VIEW retail_sales.sales.sales_summary_view TO `sales_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md ## 7.2 Grant HR team full ownership-style access to the HR catalog

-- COMMAND ----------

GRANT USE CATALOG ON CATALOG retail_hr TO `hr_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_hr.hr TO `hr_user@retailcorp.com`;

-- ALL PRIVILEGES = SELECT + MODIFY + CREATE + ... everything short of ownership transfer
GRANT ALL PRIVILEGES ON SCHEMA retail_hr.hr TO `hr_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md ## 7.3 Grant FINANCE team read access to Finance + cross-catalog reporting access

-- COMMAND ----------

GRANT USE CATALOG ON CATALOG retail_finance TO `finance_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_finance.finance TO `finance_user@retailcorp.com`;
GRANT SELECT ON SCHEMA retail_finance.finance TO `finance_user@retailcorp.com`;

-- Finance also needs revenue numbers from Sales -> grant narrow, view-only access
GRANT USE CATALOG ON CATALOG retail_sales TO `finance_user@retailcorp.com`;
GRANT USE SCHEMA  ON SCHEMA  retail_sales.sales TO `finance_user@retailcorp.com`;
GRANT SELECT ON VIEW retail_sales.sales.sales_summary_view TO `finance_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md ## 7.4 Admin — full control (typically granted once via account/metastore admin role)

-- COMMAND ----------

GRANT ALL PRIVILEGES ON CATALOG retail_sales   TO `admin_user@retailcorp.com`;
GRANT ALL PRIVILEGES ON CATALOG retail_hr      TO `admin_user@retailcorp.com`;
GRANT ALL PRIVILEGES ON CATALOG retail_finance TO `admin_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC Each `GRANT` succeeds silently. Verify with `SHOW GRANTS`:

-- COMMAND ----------

SHOW GRANTS ON TABLE retail_sales.sales.orders;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | principal | action_type | object_type | object_key |
-- MAGIC |---|---|---|---|
-- MAGIC | sales_user@retailcorp.com | SELECT | TABLE | retail_sales.sales.orders |
-- MAGIC | sales_user@retailcorp.com | MODIFY | TABLE | retail_sales.sales.orders |
-- MAGIC | admin_user@retailcorp.com | ALL PRIVILEGES | CATALOG | retail_sales |

-- COMMAND ----------

SHOW GRANTS `hr_user@retailcorp.com` ON CATALOG retail_hr;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | principal | action_type | object_type | object_key |
-- MAGIC |---|---|---|---|
-- MAGIC | hr_user@retailcorp.com | USE CATALOG | CATALOG | retail_hr |
-- MAGIC
-- MAGIC ## Talking Points
-- MAGIC - `SELECT` = read-only. `MODIFY` = `INSERT`/`UPDATE`/`DELETE`. `ALL PRIVILEGES` = everything
-- MAGIC   (short of transferring ownership, which needs a separate `ALTER ... OWNER TO`).
-- MAGIC - Grants are additive and can be scoped at any level (Catalog, Schema, Table, View, Volume,
-- MAGIC   Column via masking, Row via row filters) — always grant at the **narrowest** level that satisfies
-- MAGIC   the business need (least privilege).
-- MAGIC - Best practice in real deployments: grant to **account-level groups** (`sales_team`), not
-- MAGIC   individual users — shown in `security_demo/`.
