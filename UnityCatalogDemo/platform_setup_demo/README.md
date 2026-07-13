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

## With Catalog vs Without Unity Catalog — Side by Side

Same idea as the quickstart demo's cheat sheet, but for the platform/setup layer specifically —
this is the "why do we even need to do steps 27 and 30?" answer in one glance.

| Concept | ❌ Without Unity Catalog (Hive Metastore) | ✅ With Unity Catalog | Command / Action (with UC) |
|---|---|---|---|
| **Metastore** | No explicit object to create — each workspace silently has its own built-in one | Created **once** per region in Account Console, then explicitly attached to every workspace that should share it | Account Console → Create Metastore |
| **Scope of metadata** | Local to a single workspace; another workspace can't see or reuse it | Shared automatically across every attached workspace in that region | `SELECT CURRENT_METASTORE();` |
| **Cluster requirements** | Any cluster, any access mode works — nothing to configure | Must use **Single User** or **Shared** access mode + DBR **11.3 LTS+**; a legacy "No Isolation Shared" cluster can't see UC objects at all | Compute → Create Compute → Access Mode |
| **Cloud storage access** | Set up ad hoc, per cluster: instance profiles, `dbutils.fs.mount`, or hardcoded keys — every cluster/workspace configures it separately | Defined **once**, centrally, as a Storage Credential + External Location — every attached workspace/cluster inherits the same access automatically | `CREATE STORAGE CREDENTIAL`, `CREATE EXTERNAL LOCATION` |
| **Who can grant storage access** | Whoever configures the cluster (often just a workspace admin) — no per-path control | A Metastore admin controls the credential; regular users only ever get scoped grants like `CREATE EXTERNAL TABLE`/`READ FILES` on one External Location — they never touch the IAM role directly | `GRANT ... ON EXTERNAL LOCATION ...` |
| **Consistency across workspaces** | Each workspace admin re-does cluster + storage setup independently — configuration drift is common | One Storage Credential/External Location, reused by every attached workspace — no drift, no re-work | Inherent to the shared-Metastore architecture |
| **Auditing setup changes** | Only whatever your cloud provider logs (e.g. CloudTrail) — nothing at the Databricks level | Metastore/credential/location are governed objects with owners, comments, and a queryable audit trail | `system.access.audit` |

**The takeaway to say out loud:** "Steps 27 and 30 aren't extra bureaucracy — they replace work
every workspace admin used to redo by hand (mounts, instance profiles, per-cluster IAM) with one
setup that every workspace, cluster, and user then just inherits for free."

## After This Demo

Continue into `../quickstart_demo/` (20–25 min, catalogs/schemas/tables/views/RBAC/lineage) or the
full `../README.md` demo — both assume the Metastore, cluster, and storage access built here
already exist.
