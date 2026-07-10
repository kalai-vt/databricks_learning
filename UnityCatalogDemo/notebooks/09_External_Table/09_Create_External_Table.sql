-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 9 — External Locations, Storage Credentials & External Tables
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC Sometimes data must **stay in a specific cloud storage path** that Unity Catalog does not own —
-- MAGIC e.g. Finance's ledger extracts are produced by an upstream SAP export job that writes directly to
-- MAGIC `s3://retailcorp-finance-raw/ledger/`, and must remain there for the Finance team's other tools.
-- MAGIC This is exactly what **External Tables** are for.
-- MAGIC
-- MAGIC Three building blocks work together:
-- MAGIC
-- MAGIC | Object | Purpose |
-- MAGIC |---|---|
-- MAGIC | **Storage Credential** | A cloud IAM role/service principal that Unity Catalog is allowed to assume to read/write a cloud storage account. Created once by an admin. |
-- MAGIC | **External Location** | A named, governable pointer: "this cloud storage *path* + this *storage credential* = allowed to be used by Unity Catalog." Also created by an admin. |
-- MAGIC | **External Table** | A table whose `LOCATION` points inside an External Location. Unity Catalog manages **metadata & permissions only** — the data files stay exactly where they are. |
-- MAGIC
-- MAGIC ```
-- MAGIC Storage Credential  (IAM Role: unity-catalog-finance-role)
-- MAGIC        │
-- MAGIC        ▼
-- MAGIC External Location   (s3://retailcorp-finance-raw/ledger/)
-- MAGIC        │
-- MAGIC        ▼
-- MAGIC External Table       retail_finance.finance.finance_ledger
-- MAGIC ```
-- MAGIC
-- MAGIC **Key difference from a Managed Table:** `DROP TABLE` on an external table deletes only the
-- MAGIC Unity Catalog *metadata* — the underlying files in cloud storage are **not** deleted.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 9.1 Create a Storage Credential (admin operation — reference only)
-- MAGIC ```sql
-- MAGIC CREATE STORAGE CREDENTIAL IF NOT EXISTS finance_storage_credential
-- MAGIC WITH ( AWS_IAM_ROLE 'arn:aws:iam::<account-id>:role/unity-catalog-finance-role' )
-- MAGIC COMMENT 'Assumed by Unity Catalog to access the Finance department raw storage bucket';
-- MAGIC ```
-- MAGIC This requires the `CREATE STORAGE CREDENTIAL` privilege on the Metastore, normally reserved for
-- MAGIC platform/cloud admins because it grants direct cloud IAM trust.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 9.2 Create an External Location (admin operation — reference only)
-- MAGIC ```sql
-- MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS finance_raw_location
-- MAGIC URL 's3://retailcorp-finance-raw/ledger/'
-- MAGIC WITH (STORAGE CREDENTIAL finance_storage_credential)
-- MAGIC COMMENT 'Finance ledger extracts landed by the upstream SAP export job';
-- MAGIC ```
-- MAGIC Verify (safe to run, read-only):

-- COMMAND ----------

SHOW EXTERNAL LOCATIONS;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | name | url | credential_name |
-- MAGIC |---|---|---|
-- MAGIC | finance_raw_location | s3://retailcorp-finance-raw/ledger/ | finance_storage_credential |
-- MAGIC
-- MAGIC *(In a fresh sandbox workspace with no External Locations configured yet, this may return zero rows
-- MAGIC — that's expected; it's shown here for completeness of the demo narrative.)*

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 9.3 Create the External Table
-- MAGIC Once the External Location exists and we've been granted `CREATE EXTERNAL TABLE` on it, any SQL
-- MAGIC developer can register an external table over the existing files — no data movement required.

-- COMMAND ----------

USE CATALOG retail_finance;
USE SCHEMA finance;

CREATE TABLE IF NOT EXISTS finance_ledger (
  sale_id   STRING,
  order_id  STRING,
  sale_date DATE,
  amount    DECIMAL(10,2),
  region    STRING,
  channel   STRING
)
COMMENT 'External table: finance ledger extract, data physically owned by the Finance department bucket'
LOCATION 's3://retailcorp-finance-raw/ledger/'
-- USING DELTA is optional here; external tables can also be CSV/Parquet/JSON with the right USING clause

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC `CREATE TABLE` succeeds. Confirm it is external, not managed:

-- COMMAND ----------

DESCRIBE TABLE EXTENDED finance_ledger;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output (abridged)
-- MAGIC | col_name | data_type |
-- MAGIC |---|---|
-- MAGIC | sale_id | string |
-- MAGIC | ... | ... |
-- MAGIC | Type | **EXTERNAL** |
-- MAGIC | Location | s3://retailcorp-finance-raw/ledger/ |
-- MAGIC
-- MAGIC Compare this to `retail_sales.sales.customers` from Notebook 4, which showed `Type = MANAGED`.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - Managed vs. External is decided purely by whether you supply a `LOCATION` clause.
-- MAGIC - External tables are how Unity Catalog governs data that **must** stay in a specific bucket for
-- MAGIC   compliance, cost allocation, or integration with non-Databricks tools.
-- MAGIC - Storage Credentials and External Locations are the **only** two objects in Unity Catalog that
-- MAGIC   directly touch cloud IAM — treat granting `CREATE EXTERNAL LOCATION`/`CREATE STORAGE CREDENTIAL`
-- MAGIC   as a high-trust, admin-only privilege.
