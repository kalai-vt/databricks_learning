# Unity Catalog Platform Setup — Short Demo (Section 5 Companion)

Matches this 6-lecture curriculum section (50 min of video) with a **~30 min hands-on demo**:

| # | Lecture | File | Time | Hands-on? |
|---|---|---|---|---|
| 25 | Introduction to Unity Catalog | `01_intro_concepts.md` | 3 min | Concept |
| 26 | UC / Hive Metastore Object Model | `01_intro_concepts.md` | 2 min | Concept + 1 SQL check |
| 27 | Create Unity Catalog Metastore | `02_create_metastore_steps.md` | 8 min | ✅ Account Console + SQL |
| 28 | Cluster Configurations for UC | `03_cluster_configuration.md` | 5 min | ✅ Create a cluster + SQL check |
| 29 | Configure Access to Cloud Storage — Lecture | `04_storage_credential_external_location_concepts.md` | 4 min | Concept |
| 30 | Configure Access to Cloud Storage — Demo | `05_configure_cloud_storage_demo.sql` | 8 min | ✅ Full hands-on |

**Total: ~30 minutes.** This is the *platform/admin setup* side of Unity Catalog — how the
Metastore, compute, and cloud storage access get wired up in the first place. It's a prerequisite
companion to the main `../README.md` demo, which assumes all of this already exists and focuses on
catalogs/schemas/tables/grants/lineage for day-to-day SQL developers.

## Who Needs Admin Access

Topics 27 and 30 involve real cloud IAM and Databricks Account Console actions — normally done
once by a platform/cloud admin, not by every learner. If you don't have Account Admin or cloud
console access:
- **Still do:** the verification SQL (`SELECT CURRENT_METASTORE();`, `SHOW CATALOGS;`,
  `SHOW STORAGE CREDENTIALS;`) against a workspace where an admin has already completed setup.
- **Watch/follow along:** the console click-paths, so you understand what your platform team did
  and why, even if you can't click through it yourself today.

Topic 28 (cluster configuration) typically **can** be done hands-on by anyone with cluster-create
permission in a workspace, even without account admin rights.

## Suggested Delivery Order

1. **Intro + Object Model** (`01_intro_concepts.md`) — set up the mental model with the ASCII
   diagram: Hive Metastore is workspace-scoped and 2-level; Unity Catalog is account-scoped,
   shared across workspaces, and 3-level.
2. **Create Metastore** (`02_create_metastore_steps.md`) — walk the Account Console steps (live if
   you have access, otherwise screen-share/narrate), then prove it from SQL.
3. **Cluster Configuration** (`03_cluster_configuration.md`) — create a Single User or Shared
   cluster live, run `SHOW CATALOGS;` on it to prove UC is visible. If you have an old "No
   Isolation Shared" cluster around, show the contrast — this is the single most common
   "why doesn't my query work" gotcha for beginners.
4. **Storage Credential & External Location concepts** (`04_...md`) — quick diagram: IAM Role →
   Storage Credential → External Location → External Table/Volume.
5. **Configure Cloud Storage demo** (`05_...sql`) — the full hands-on: create the credential and
   location (UI or SQL), then prove it works by creating a real External Table and querying it.

## After This Demo

Continue into `../quickstart_demo/` (20–25 min, catalogs/schemas/tables/views/RBAC/lineage) or the
full `../README.md` demo — both assume the Metastore, cluster, and storage access built here
already exist.
