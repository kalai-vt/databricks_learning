-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Notebook 1 — The Unity Catalog Metastore
-- MAGIC
-- MAGIC ## Explanation
-- MAGIC A **Metastore** is the top-level container in Unity Catalog. It stores metadata about
-- MAGIC every catalog, schema, table, view, volume, and the permissions attached to them.
-- MAGIC
-- MAGIC Key facts to tell the audience:
-- MAGIC 1. There is normally **one Metastore per cloud region** (e.g. one for `us-east-1`, one for `eu-west-1`).
-- MAGIC 2. A Metastore is created **once** by an Account Admin at the **Account Console** level (or via the
-- MAGIC    Databricks Account API / Terraform) — it is **not** created with a SQL statement, because it sits
-- MAGIC    *above* the workspace and can be shared by many workspaces in the same region.
-- MAGIC 3. Workspaces are then **attached (assigned)** to a Metastore. Every catalog you create in that
-- MAGIC    workspace lives inside the attached Metastore.
-- MAGIC 4. A Metastore also owns a **default managed storage location** (a cloud storage container) where
-- MAGIC    Managed Tables/Volumes physically store their data unless a catalog/schema overrides it.
-- MAGIC
-- MAGIC For this demo, the Metastore already exists and our workspace is attached to it (this is normally
-- MAGIC done once by the platform team). We only need to **verify** it from SQL.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## How a Metastore is actually created (reference only — run in Account Console, not here)
-- MAGIC ```text
-- MAGIC Account Console → Data (Catalogs) → Create Metastore
-- MAGIC   Name:            primary-metastore-us-east-1
-- MAGIC   Region:          us-east-1
-- MAGIC   Storage bucket:  s3://retailcorp-uc-metastore-root/
-- MAGIC   IAM role:        arn:aws:iam::<account-id>:role/unity-catalog-metastore-role
-- MAGIC
-- MAGIC Account Console → Workspaces → <workspace> → Assign Metastore
-- MAGIC ```
-- MAGIC This is a **one-time, admin-only** setup step per region. As an SQL Developer/BI Developer,
-- MAGIC you will almost never touch this — but you must understand it exists.

-- COMMAND ----------

-- Verify which Metastore this workspace is currently attached to
SELECT CURRENT_METASTORE();

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Expected Output
-- MAGIC | current_metastore() |
-- MAGIC |---|
-- MAGIC | aws:us-east-1:1234abcd-5678-efgh-9012-ijklmnopqrst |
-- MAGIC
-- MAGIC The value is the Metastore's unique ID for this region — proof that Unity Catalog is active.

-- COMMAND ----------

-- List every catalog visible in this Metastore (before we create our own)
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
-- MAGIC * `main` — default starter catalog created automatically with every new Metastore.
-- MAGIC * `system` — read-only catalog exposing Unity Catalog's own operational data (audit logs, lineage,
-- MAGIC   billing, access) — we will use this in the Lineage Demo notebook.
-- MAGIC * `samples` — Databricks-provided sample datasets.
-- MAGIC * `hive_metastore` — the **legacy** workspace-local Hive Metastore, still visible for backward
-- MAGIC   compatibility. This is exactly the system Unity Catalog was built to replace — see the
-- MAGIC   concepts doc (`docs/01_concepts_overview.md`) for the full comparison.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Talking Points
-- MAGIC - Metastore = the "master filing cabinet" for all metadata, one per region, shared across workspaces.
-- MAGIC - Everything we do for the rest of this demo (catalogs, schemas, tables, grants, lineage) lives
-- MAGIC   **inside** this one Metastore.
-- MAGIC - Contrast with Hive Metastore, which was **local to a single workspace/cluster** — no cross-workspace
-- MAGIC   sharing, no central governance. That's problem #1 we're about to solve.
