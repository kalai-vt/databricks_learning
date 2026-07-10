-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 11 — Query Examples Across the Three-Level Namespace
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC This notebook is a grab-bag of everyday queries a SQL Developer / BI Developer would run once
-- MAGIC Unity Catalog objects exist — including a query that spans **two catalogs in a single join**,
-- MAGIC something that was awkward or impossible in a Hive-Metastore-per-workspace world.

-- COMMAND ----------

-- MAGIC %md ## 11.1 Simple fully-qualified SELECT

-- COMMAND ----------

SELECT customer_id, customer_name, city, segment
FROM retail_sales.sales.customers
WHERE segment = 'Corporate'
ORDER BY customer_name;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output (sample)
-- MAGIC | customer_id | customer_name | city | segment |
-- MAGIC |---|---|---|---|
-- MAGIC | C003 | Rohan Mehta | Delhi | Corporate |
-- MAGIC | C005 | Karan Malhotra | Pune | Corporate |
-- MAGIC | C009 | Arjun Kapoor | Jaipur | Corporate |
-- MAGIC | C013 | Siddharth Joshi | Nagpur | Corporate |
-- MAGIC | C017 | Manish Agarwal | Indore | Corporate |

-- COMMAND ----------

-- MAGIC %md ## 11.2 Revenue by product category (using the view built in Notebook 6)

-- COMMAND ----------

SELECT
  category,
  COUNT(DISTINCT order_id) AS orders,
  SUM(amount)              AS total_revenue
FROM retail_sales.sales.sales_summary_view
GROUP BY category
ORDER BY total_revenue DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output (sample)
-- MAGIC | category | orders | total_revenue |
-- MAGIC |---|---|---|
-- MAGIC | Electronics | 6 | 20393.00 |
-- MAGIC | Footwear | 2 | 7298.00 |
-- MAGIC | Apparel | 3 | 3792.00 |
-- MAGIC | ... | ... | ... |

-- COMMAND ----------

-- MAGIC %md ## 11.3 Cross-catalog join — Sales revenue attributed to the department that owns it
-- MAGIC This single query reads from **two different catalogs** (`retail_sales` and `retail_hr`) in one
-- MAGIC statement — Unity Catalog's three-level namespace makes this trivial, whereas classic Hive
-- MAGIC Metastore had no concept of "catalog" to cross in the first place.

-- COMMAND ----------

SELECT
  d.department_name,
  d.manager_name,
  ROUND(SUM(s.amount), 2) AS total_sales_amount
FROM retail_sales.sales.sales_summary_view s
CROSS JOIN retail_hr.hr.departments d
WHERE d.department_name = 'Sales'
GROUP BY d.department_name, d.manager_name;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | department_name | manager_name | total_sales_amount |
-- MAGIC |---|---|---|
-- MAGIC | Sales | Rajesh Kumar | 35396.00 |
-- MAGIC
-- MAGIC *(Illustrative CROSS JOIN used purely to show a two-catalog query in one statement; a real report
-- MAGIC would use a proper sales-rep-to-department mapping key.)*

-- COMMAND ----------

-- MAGIC %md ## 11.4 Metadata queries via information_schema (works like ANSI SQL)

-- COMMAND ----------

SELECT table_catalog, table_schema, table_name, table_type
FROM retail_sales.information_schema.tables
ORDER BY table_type, table_name;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | table_catalog | table_schema | table_name | table_type |
-- MAGIC |---|---|---|---|
-- MAGIC | retail_sales | sales | customers | MANAGED |
-- MAGIC | retail_sales | sales | orders | MANAGED |
-- MAGIC | retail_sales | sales | products | MANAGED |
-- MAGIC | retail_sales | sales | sales | MANAGED |
-- MAGIC | retail_sales | sales | sales_summary_view | VIEW |

-- COMMAND ----------

-- MAGIC %md ## 11.5 DESCRIBE / SHOW quick reference

-- COMMAND ----------

SHOW TABLES IN retail_sales.sales;
-- DESCRIBE TABLE retail_sales.sales.orders;
-- DESCRIBE TABLE EXTENDED retail_sales.sales.orders;
-- SHOW COLUMNS IN retail_sales.sales.orders;
-- SHOW CREATE TABLE retail_sales.sales.orders;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - Fully-qualified `catalog.schema.object` names remove any ambiguity — critical when the same table
-- MAGIC   name (`sales`) could exist in many schemas.
-- MAGIC - `information_schema` gives every catalog a self-documenting, query-able metadata layer, useful for
-- MAGIC   building custom data catalogs, lineage tools, or documentation generators.
-- MAGIC - This is also exactly the layer BI tools like Power BI / Tableau query when you connect them via
-- MAGIC   Databricks SQL — they see catalogs and schemas as a normal database/schema tree.
