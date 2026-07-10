-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 6 — Creating Views
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC A **View** is a saved SQL query registered in Unity Catalog like any other object
-- MAGIC (`catalog.schema.view_name`). It stores **no data of its own** — every time it's queried, the
-- MAGIC underlying tables are re-read live. Views are governed by GRANT/REVOKE exactly like tables, which
-- MAGIC makes them a powerful, lightweight way to:
-- MAGIC - Pre-join and simplify data for BI tools (Power BI, Tableau).
-- MAGIC - Expose only a safe subset of columns (e.g. hide `salary` from a general HR view).
-- MAGIC - Build the next node in a **lineage graph** (see Notebook 12).
-- MAGIC
-- MAGIC We'll create `sales_summary_view` — this becomes the star of our Lineage Demo later.

-- COMMAND ----------

USE CATALOG retail_sales;
USE SCHEMA sales;

CREATE OR REPLACE VIEW sales_summary_view
COMMENT 'One row per order: customer, product and sale amount — feeds the Power BI revenue dashboard'
AS
SELECT
  o.order_id,
  c.customer_id,
  c.customer_name,
  c.state,
  p.product_id,
  p.product_name,
  p.category,
  o.order_date,
  o.quantity,
  s.amount,
  s.region,
  s.channel
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products  p ON o.product_id  = p.product_id
JOIN sales     s ON s.order_id    = o.order_id
WHERE o.order_status = 'Delivered';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC `CREATE VIEW` succeeds silently. Preview the data:

-- COMMAND ----------

SELECT * FROM sales_summary_view ORDER BY order_date LIMIT 10;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output (sample)
-- MAGIC | order_id | customer_name | product_name | order_date | amount | region |
-- MAGIC |---|---|---|---|---|---|
-- MAGIC | O1001 | Aarav Sharma | Wireless Mouse | 2023-01-05 | 1598.00 | West |
-- MAGIC | O1002 | Priya Nair | Cotton T-Shirt | 2023-01-08 | 599.00 | South |
-- MAGIC | ... | ... | ... | ... | ... | ... |
-- MAGIC
-- MAGIC 18 rows returned (20 orders minus the 1 `Cancelled` and 1 `Returned` order).

-- COMMAND ----------

-- MAGIC %md
-- MAGIC A second view for the HR side, this time demonstrating **column masking by omission** — we simply
-- MAGIC leave `salary` and `email` out of the view so an HR view consumer doesn't automatically see them.

-- COMMAND ----------

USE CATALOG retail_hr;
USE SCHEMA hr;

CREATE OR REPLACE VIEW employee_department_view
COMMENT 'Employee directory without sensitive salary/email columns'
AS
SELECT
  e.employee_id,
  e.employee_name,
  e.job_title,
  e.hire_date,
  d.department_name,
  d.location,
  d.manager_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- COMMAND ----------

SELECT * FROM employee_department_view LIMIT 10;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output (sample)
-- MAGIC | employee_id | employee_name | job_title | department_name |
-- MAGIC |---|---|---|---|
-- MAGIC | E101 | Rajesh Kumar | Sales Manager | Sales |
-- MAGIC | E102 | Sunita Rao | HR Manager | Human Resources |
-- MAGIC | ... | ... | ... | ... |
-- MAGIC
-- MAGIC Note: `salary` and `email` are not selectable through this view at all — a clean way to give
-- MAGIC broad read access without exposing PII/compensation data.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - Views live in the same namespace as tables: `SHOW TABLES` will even list them (flagged as views).
-- MAGIC - Because Unity Catalog tracks the view's query text, it can compute **column-level lineage**
-- MAGIC   automatically — showing that `sales_summary_view.amount` came from `sales.amount`.
-- MAGIC - Views are the cleanest way to implement "need-to-know" access without duplicating data.
