# 27 — Create a Unity Catalog Metastore (~8–10 min hands-on)

**Who can do this:** Account Admin, in the **Account Console** (`accounts.cloud.databricks.com`)
— not inside a workspace, and not with SQL. This is the one manual, click-through setup step in
the whole Unity Catalog story. If you don't have Account Admin rights, follow along as a guided
walkthrough — you'll still run the verification SQL at the end on a real workspace.

## Prerequisites (5 min, do this first — in your cloud console, e.g. AWS)

1. **Create an S3 bucket** to act as the Metastore's root storage, e.g. `retailcorp-uc-metastore-root`.
   This is where Managed Tables/Volumes will physically store data by default.
2. **Create an IAM role** with:
   - A trust policy that allows Databricks' own AWS account to assume it (Databricks gives you
     this exact JSON to paste when you start the Metastore-creation wizard).
   - A permissions policy granting `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`,
     `s3:ListBucket` on that bucket.

> Azure equivalent: an **Access Connector for Azure Databricks** + an ADLS Gen2 storage account.
> GCP equivalent: a **GCS bucket** + a Databricks-managed **Google Cloud service account**.

## Steps — Account Console

1. Go to `accounts.cloud.databricks.com` and sign in as an Account Admin.
2. Left sidebar → **Catalog** (or **Data**) → **Create Metastore**.
3. Fill in:
   - **Name**: e.g. `retailcorp-metastore-us-east-1`
   - **Region**: must match the region of the workspace(s) you'll attach — this is a hard
     requirement, one Metastore per region.
   - **S3 bucket path**: `s3://retailcorp-uc-metastore-root/`
   - **IAM role ARN**: the role you created above.
4. Click **Create**.
5. You'll be prompted to **assign workspaces** — select one or more workspaces in that region and
   click **Enable**. A workspace can only be attached to one Metastore at a time.

## Verify From SQL (back inside the workspace)

```sql
SELECT CURRENT_METASTORE();   -- returns the Metastore's unique ID — proof it's attached
SHOW CATALOGS;                -- main, system, samples, hive_metastore now appear automatically
```

## Talking Points

- This is a **one-time, region-wide** setup step — most SQL developers/data engineers will never
  do this themselves; an admin does it once and everyone else just inherits it.
- A common mistake: trying to create a second Metastore in a region that already has one attached
  to your workspace. Check **Account Console → Workspaces → \<workspace\> → Metastore** first.
- Everything you build for the rest of the course (catalogs, schemas, tables, grants) lives
  *inside* this one Metastore.
