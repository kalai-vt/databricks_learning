-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 8 — Revoking Permissions
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC `REVOKE` removes a previously granted privilege. It uses the exact same object/privilege syntax as
-- MAGIC `GRANT`, just with the keyword flipped. Revoking a broader privilege (e.g. `USE CATALOG`) blocks
-- MAGIC access even if narrower privileges (e.g. `SELECT` on a table) technically remain — remember the
-- MAGIC "layered lock": **all** levels of the hierarchy must be satisfied simultaneously.
-- MAGIC
-- MAGIC ### Scenario
-- MAGIC The Finance department decides `finance_user@retailcorp.com` should no longer be able to write to
-- MAGIC anything in `retail_sales` (they only ever had `SELECT` there, but let's be explicit), and a
-- MAGIC contractor's temporary access to the `products` table is ending.

-- COMMAND ----------

-- Revoke a single table-level privilege
REVOKE SELECT ON TABLE retail_sales.sales.products FROM `sales_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC `REVOKE` succeeds silently. Verify it's gone:

-- COMMAND ----------

SHOW GRANTS `sales_user@retailcorp.com` ON TABLE retail_sales.sales.products;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | principal | action_type | object_type | object_key |
-- MAGIC |---|---|---|---|
-- MAGIC *(empty result set — no rows returned, confirming the SELECT grant is gone)*

-- COMMAND ----------

-- Re-grant it back so the rest of the demo (Notebook 11 Query Examples) keeps working
GRANT SELECT ON TABLE retail_sales.sales.products TO `sales_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Full lock-out example — revoke at the catalog level
-- MAGIC This is the most common way admins fully cut off a department's access, e.g. an employee
-- MAGIC transferring out of Finance:

-- COMMAND ----------

REVOKE USE CATALOG ON CATALOG retail_finance FROM `finance_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC From this point, **every** query `finance_user@retailcorp.com` runs against `retail_finance.*`
-- MAGIC fails with:
-- MAGIC ```text
-- MAGIC Error: [INSUFFICIENT_PERMISSIONS] User does not have USE CATALOG on Catalog 'retail_finance'.
-- MAGIC ```
-- MAGIC even though their table-level `SELECT` grants technically still exist underneath — proving that
-- MAGIC **every level of the hierarchy is checked independently**.

-- COMMAND ----------

-- Restore access for the rest of the demo
GRANT USE CATALOG ON CATALOG retail_finance TO `finance_user@retailcorp.com`;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - `REVOKE` never cascades automatically to child objects' *other* grants — it only removes the
-- MAGIC   specific privilege/object pair you name.
-- MAGIC - Revoking a parent-level `USE CATALOG`/`USE SCHEMA` is the fastest way to fully block a principal
-- MAGIC   without hunting down every table grant individually.
-- MAGIC - Always verify with `SHOW GRANTS` after a revoke during a real incident response — don't assume.
