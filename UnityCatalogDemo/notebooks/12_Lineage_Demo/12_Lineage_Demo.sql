-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 12 — Automatic Data Lineage
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC Unity Catalog automatically captures **table-level and column-level lineage** for every query it
-- MAGIC executes — no extra tagging, no separate lineage tool, no manual documentation. It works by
-- MAGIC analyzing the query plan of every SQL statement, notebook cell, DLT/Lakeflow pipeline, and Job that
-- MAGIC reads or writes a Unity Catalog table/view.
-- MAGIC
-- MAGIC ### Our lineage chain for this demo
-- MAGIC ```
-- MAGIC retail_sales.sales.customers ─┐
-- MAGIC                                ├─▶ retail_sales.sales.sales_summary_view ─▶ Power BI Dashboard
-- MAGIC retail_sales.sales.orders ────┤
-- MAGIC retail_sales.sales.products ──┤
-- MAGIC retail_sales.sales.sales ─────┘
-- MAGIC ```
-- MAGIC We already created every link in this chain (Notebooks 4-6). This notebook shows how to **see**
-- MAGIC that lineage both visually (Catalog Explorer) and programmatically (system tables).

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 12.1 View lineage visually in Catalog Explorer (click-through during the live demo)
-- MAGIC ```text
-- MAGIC Catalog Explorer → retail_sales → sales → sales_summary_view → "Lineage" tab
-- MAGIC ```
-- MAGIC You will see an interactive graph:
-- MAGIC - **Upstream**: `customers`, `orders`, `products`, `sales` tables feeding into the view.
-- MAGIC - **Downstream**: any notebook, job, dashboard, or BI tool connection that has queried the view
-- MAGIC   (e.g. a Power BI dataset connected via Databricks SQL) appears automatically the first time it
-- MAGIC   runs a query against it — nothing to configure.
-- MAGIC - Switching to the **Columns** sub-tab shows column-level lineage, e.g. `sales_summary_view.amount`
-- MAGIC   traces directly back to `sales.amount`.

-- COMMAND ----------

-- MAGIC %md ## 12.2 Query lineage programmatically via System Tables
-- MAGIC Unity Catalog exposes its own operational metadata (including lineage) as regular queryable tables
-- MAGIC in the built-in `system` catalog — enabling custom lineage dashboards or governance automation.

-- COMMAND ----------

SELECT
  source_table_full_name,
  target_table_full_name,
  source_type,
  target_type,
  event_time
FROM system.access.table_lineage
WHERE target_table_full_name = 'retail_sales.sales.sales_summary_view'
ORDER BY event_time DESC
LIMIT 10;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | source_table_full_name | target_table_full_name | source_type | target_type |
-- MAGIC |---|---|---|---|
-- MAGIC | retail_sales.sales.customers | retail_sales.sales.sales_summary_view | TABLE | VIEW |
-- MAGIC | retail_sales.sales.orders | retail_sales.sales.sales_summary_view | TABLE | VIEW |
-- MAGIC | retail_sales.sales.products | retail_sales.sales.sales_summary_view | TABLE | VIEW |
-- MAGIC | retail_sales.sales.sales | retail_sales.sales.sales_summary_view | TABLE | VIEW |
-- MAGIC
-- MAGIC *(`system.access.table_lineage` requires the system schema to be enabled for the Metastore by an
-- MAGIC admin — a one-time setup step. If it returns no rows in your sandbox, use the Catalog Explorer UI
-- MAGIC view instead, which always works.)*

-- COMMAND ----------

-- MAGIC %md ## 12.3 Connecting Power BI to complete the downstream chain
-- MAGIC 1. In Power BI Desktop: **Get Data → Databricks** → enter the SQL Warehouse hostname/HTTP path.
-- MAGIC 2. Navigate to `retail_sales → sales → sales_summary_view` and load it as a dataset.
-- MAGIC 3. Build a simple revenue-by-category bar chart and publish the dashboard.
-- MAGIC 4. Back in Catalog Explorer, refresh the `sales_summary_view` lineage graph — the Power BI
-- MAGIC    dashboard now appears as a **downstream node**, captured automatically the moment the connection
-- MAGIC    first queried the view.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - Lineage is **automatic and retroactive-free** — it only starts recording from the moment Unity
-- MAGIC   Catalog governs the object, but requires zero developer effort once it does.
-- MAGIC - This is invaluable for **impact analysis** ("if I change this table's schema, what breaks?") and
-- MAGIC   **compliance/audit** ("prove where this number in the CFO's dashboard came from").
-- MAGIC - Under Hive Metastore, this kind of lineage either didn't exist or required a bolt-on third-party
-- MAGIC   catalog tool (e.g. Apache Atlas) with its own separate maintenance burden.
