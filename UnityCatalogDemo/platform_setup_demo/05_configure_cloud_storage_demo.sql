-- =====================================================================
-- 30 — Configure Access to Cloud Storage: DEMO (~8-10 min hands-on)
-- Prereqs: 02_create_metastore_steps.md already done (Metastore exists);
-- a Unity-Catalog-enabled cluster/SQL Warehouse (see 03) is running.
-- =====================================================================


-- ── PART A: In your cloud console (AWS example) — do this first ──────
-- 1. Create (or pick) an S3 bucket for external data, e.g.
--      s3://retailcorp-external-data/
-- 2. In Databricks: Catalog Explorer -> External Data -> Credentials ->
--    "Create credential" -> this screen GENERATES the exact IAM trust
--    policy JSON (with a unique External ID) for you to paste into AWS.
-- 3. In AWS IAM: create a role using that generated trust policy, and
--    attach a permissions policy granting:
--      s3:GetObject, s3:PutObject, s3:DeleteObject, s3:ListBucket
--    scoped to the bucket above.
-- 4. Back in the Databricks "Create credential" screen: paste the Role
--    ARN, click "Test connection", then "Create".
--
-- Azure equivalent: create an Access Connector for Azure Databricks and
-- reference it. GCP equivalent: Databricks auto-provisions a service
-- account for you to grant bucket IAM permissions to.


-- ── PART B: Register the External Location (Databricks UI or SQL) ────
-- UI path: Catalog Explorer -> External Data -> External Locations ->
--          "Create location" -> URL + pick the credential from Part A.
--
-- Equivalent SQL (run as an admin/privileged user):
-- CREATE STORAGE CREDENTIAL IF NOT EXISTS retailcorp_ext_credential
-- WITH ( AWS_IAM_ROLE 'arn:aws:iam::<account-id>:role/unity-catalog-external-role' )
-- COMMENT 'Assumed by Unity Catalog to access retailcorp-external-data';

-- CREATE EXTERNAL LOCATION IF NOT EXISTS retailcorp_external_location
-- URL 's3://retailcorp-external-data/'
-- WITH (STORAGE CREDENTIAL retailcorp_ext_credential)
-- COMMENT 'General-purpose external bucket for the demo';


-- ── PART C: Verify from SQL (safe to run — read-only) ─────────────────
SHOW STORAGE CREDENTIALS;
SHOW EXTERNAL LOCATIONS;
DESCRIBE EXTERNAL LOCATION retailcorp_external_location;


-- ── PART D: Prove it works — list files, then create + query an
--            External Table inside the location ────────────────────
LIST 's3://retailcorp-external-data/';

-- Reuse the catalog/schema from quickstart_demo if you already built it,
-- otherwise create a scratch one:
CREATE CATALOG IF NOT EXISTS uc_quickstart;
CREATE SCHEMA IF NOT EXISTS uc_quickstart.retail;

CREATE TABLE IF NOT EXISTS uc_quickstart.retail.storage_test (
  id   INT,
  note STRING
)
COMMENT 'Proves the External Location + Storage Credential actually work'
LOCATION 's3://retailcorp-external-data/storage_test/';

INSERT INTO uc_quickstart.retail.storage_test VALUES
  (1, 'Hello from an External Table backed by our new Storage Credential!');

SELECT * FROM uc_quickstart.retail.storage_test;

DESCRIBE TABLE EXTENDED uc_quickstart.retail.storage_test;
-- Confirm: Type = EXTERNAL, Location = s3://retailcorp-external-data/storage_test/


-- ── Cleanup (optional) ─────────────────────────────────────────────────
-- DROP TABLE IF EXISTS uc_quickstart.retail.storage_test;
-- DROP EXTERNAL LOCATION IF EXISTS retailcorp_external_location;
-- DROP STORAGE CREDENTIAL IF EXISTS retailcorp_ext_credential;


-- ── Talking Points ─────────────────────────────────────────────────────
-- 1. Two admin objects (Storage Credential, External Location), created
--    once, unlock unlimited External Tables/Volumes for everyone else.
-- 2. DROP TABLE on storage_test removes ONLY Unity Catalog metadata —
--    the actual file under s3://retailcorp-external-data/storage_test/
--    is untouched, exactly like the External Table concept from the
--    main demo (see ../notebooks/09_External_Table).
-- 3. "Test connection" in the UI at credential/location creation time
--    is the fastest way to catch a broken IAM trust policy before it
--    becomes a confusing runtime error for someone else later.
