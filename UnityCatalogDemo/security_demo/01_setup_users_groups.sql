-- =====================================================================
-- 01_setup_users_groups.sql
-- Purpose : Reference for setting up the demo's identity model.
--
-- Users/groups in Databricks are account-level objects managed in the
-- Account Console (or synced from your IdP via SCIM) — they are NOT
-- created with SQL. This file documents what to set up before the live
-- demo, plus the SQL that then GRANTs privileges to those identities.
-- =====================================================================

-- MAGIC %md
-- Step 1 — Create four demo users in Account Console > User Management
-- (or reuse existing workspace users and just rename references below):
--
--   admin_user@retailcorp.com     -> add as Account Admin / Metastore Admin
--   sales_user@retailcorp.com     -> regular user, member of group `sales_team`
--   hr_user@retailcorp.com        -> regular user, member of group `hr_team`
--   finance_user@retailcorp.com   -> regular user, member of group `finance_team`
--
-- Step 2 — Create three account groups:
--   sales_team, hr_team, finance_team
--
-- Best practice: ALWAYS grant privileges to GROUPS, not individual users.
-- It is far easier to onboard/offboard someone by changing group
-- membership than to hunt down every individual GRANT statement.

-- ---------------------------------------------------------------------
-- Group-based grants (recommended pattern; replace the user-level
-- grants in sql_scripts/06_grant.sql with these in a real deployment)
-- ---------------------------------------------------------------------

GRANT USE CATALOG ON CATALOG retail_sales TO `sales_team`;
GRANT USE SCHEMA  ON SCHEMA  retail_sales.sales TO `sales_team`;
GRANT SELECT ON TABLE retail_sales.sales.customers TO `sales_team`;
GRANT SELECT ON TABLE retail_sales.sales.products  TO `sales_team`;
GRANT SELECT, MODIFY ON TABLE retail_sales.sales.orders TO `sales_team`;
GRANT SELECT, MODIFY ON TABLE retail_sales.sales.sales  TO `sales_team`;
GRANT SELECT ON VIEW retail_sales.sales.sales_summary_view TO `sales_team`;

GRANT USE CATALOG ON CATALOG retail_hr TO `hr_team`;
GRANT USE SCHEMA  ON SCHEMA  retail_hr.hr TO `hr_team`;
GRANT ALL PRIVILEGES ON SCHEMA retail_hr.hr TO `hr_team`;

GRANT USE CATALOG ON CATALOG retail_finance TO `finance_team`;
GRANT USE SCHEMA  ON SCHEMA  retail_finance.finance TO `finance_team`;
GRANT SELECT ON SCHEMA retail_finance.finance TO `finance_team`;
GRANT USE CATALOG ON CATALOG retail_sales TO `finance_team`;
GRANT USE SCHEMA  ON SCHEMA  retail_sales.sales TO `finance_team`;
GRANT SELECT ON VIEW retail_sales.sales.sales_summary_view TO `finance_team`;

-- Verify group membership from SQL (read-only, account-level):
-- SELECT * FROM system.access.grants WHERE principal IN ('sales_team','hr_team','finance_team');
