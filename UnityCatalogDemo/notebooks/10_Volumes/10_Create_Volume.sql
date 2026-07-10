-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 10 — Volumes (Governed Access to Non-Tabular Files)
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC A **Volume** is a Unity Catalog object for governing access to **files that are not structured
-- MAGIC tables** — CSVs waiting to be loaded, PDFs, images, model checkpoints, JSON logs, etc. Volumes sit
-- MAGIC at the same level as Tables inside a Schema: `catalog.schema.volume_name`.
-- MAGIC
-- MAGIC Before Volumes, this kind of file access was done with ungoverned DBFS mounts or `/dbfs/...`
-- MAGIC paths — invisible to Unity Catalog's permission model. Volumes bring **GRANT/REVOKE governance and
-- MAGIC audit logging to raw files**, closing that gap.
-- MAGIC
-- MAGIC | Volume Type | Behaves like |
-- MAGIC |---|---|
-- MAGIC | **Managed Volume** | Managed Table — Unity Catalog picks and owns the storage path |
-- MAGIC | **External Volume** | External Table — points at an existing path inside an External Location |
-- MAGIC
-- MAGIC We'll create a **Managed Volume** to land the raw CSV files for this demo before loading them with
-- MAGIC `COPY INTO`.

-- COMMAND ----------

USE CATALOG retail_sales;
USE SCHEMA sales;

CREATE VOLUME IF NOT EXISTS raw_files
COMMENT 'Landing zone for raw CSV files before they are loaded into managed Delta tables';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC `CREATE VOLUME` succeeds. Verify:

-- COMMAND ----------

SHOW VOLUMES IN retail_sales.sales;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | catalog | schema | volume_name |
-- MAGIC |---|---|---|
-- MAGIC | retail_sales | sales | raw_files |
-- MAGIC
-- MAGIC Every Volume exposes a filesystem-style path you can use in any Databricks file API:
-- MAGIC ```
-- MAGIC /Volumes/retail_sales/sales/raw_files/
-- MAGIC ```

-- COMMAND ----------

DESCRIBE VOLUME retail_sales.sales.raw_files;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output (abridged)
-- MAGIC | info_name | info_value |
-- MAGIC |---|---|
-- MAGIC | Volume Name | raw_files |
-- MAGIC | Type | MANAGED |
-- MAGIC | Storage Location | s3://retailcorp-uc-metastore-root/retail_sales/sales/raw_files |

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 10.1 Copy a CSV file into the Volume (run from a notebook cell, Python)
-- MAGIC ```python
-- MAGIC dbutils.fs.cp(
-- MAGIC   "file:/path/to/UnityCatalogDemo/data/customers.csv",
-- MAGIC   "/Volumes/retail_sales/sales/raw_files/customers.csv"
-- MAGIC )
-- MAGIC ```
-- MAGIC Or upload directly through **Catalog Explorer → Volumes → raw_files → Upload** (no code needed —
-- MAGIC great for a live demo click-through).

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 10.2 Read files straight out of the Volume with SQL
-- MAGIC Once `customers.csv` has been uploaded to the Volume, you can query it directly with `read_files`
-- MAGIC — no table registration needed:
-- MAGIC ```sql
-- MAGIC SELECT * FROM read_files(
-- MAGIC   '/Volumes/retail_sales/sales/raw_files/customers.csv',
-- MAGIC   format => 'csv',
-- MAGIC   header => true
-- MAGIC );
-- MAGIC ```

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 10.3 Production load pattern: COPY INTO from a Volume into a managed Delta table
-- MAGIC ```sql
-- MAGIC COPY INTO retail_sales.sales.customers
-- MAGIC FROM '/Volumes/retail_sales/sales/raw_files/customers.csv'
-- MAGIC FILEFORMAT = CSV
-- MAGIC FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true')
-- MAGIC COPY_OPTIONS ('mergeSchema' = 'true');
-- MAGIC ```
-- MAGIC `COPY INTO` is idempotent — files already loaded are automatically skipped on re-run, making it
-- MAGIC safe for scheduled incremental loads.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - Volumes = governed file storage; Tables = governed structured data. Same GRANT/REVOKE model, same
-- MAGIC   Catalog Explorer, same audit log — one consistent governance layer for **everything**.
-- MAGIC - This is what finally lets Unity Catalog govern unstructured/semi-structured data (ML model
-- MAGIC   artifacts, images for computer vision, raw landing files) alongside your tables.
-- MAGIC - Compare to Hive Metastore: raw file access was ungoverned DBFS — a major audit/compliance gap.
