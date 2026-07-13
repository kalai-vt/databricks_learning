# DBFS vs Hive Metastore vs Unity Catalog

These three get confused constantly because they all sound like "where Databricks keeps my
data" — but they solve three **different** problems and sit at different layers. This doc pins
down exactly what each one is, how they relate, and gives a 5-minute hands-on to see the
difference live.

## The One-Sentence Version

- **DBFS** = a **storage** layer — a distributed filesystem over cloud storage, for reading and
  writing raw files.
- **Hive Metastore** = a **metadata** layer — a catalog that maps table names to those files' paths.
- **Unity Catalog** = a **governance** layer — a catalog that maps table/file names to their
  storage **and** enforces who can access them, tracks lineage, and audits usage, across the
  whole account.

## What Each One Actually Is

### DBFS (Databricks File System)
A distributed filesystem **abstraction** mounted on every cluster, backed by your cloud object
storage (S3 / ADLS / GCS). It answers "how do I read/write a file?" — nothing more. It has **no
concept** of tables, schemas, or SQL-style permissions. Historically, any user on a cluster with
DBFS access could read or write **any** file under the DBFS root — there was no fine-grained
access control built into DBFS itself.

```python
# DBFS is just files — paths in, bytes out
dbutils.fs.ls("/mnt/raw-data/")
dbutils.fs.cp("file:/tmp/customers.csv", "dbfs:/mnt/raw-data/customers.csv")
```

### Hive Metastore
A **metadata catalog** — it stores table/database *definitions* (names, columns, types, and a
pointer to where the actual data files live, often on DBFS or a cloud path) so a SQL engine can
resolve `database.table` into real files. It's the "phone book," not the data itself. Scoped to a
**single workspace**, 2-level namespace (`database.table`), and its access control (table ACLs)
only takes effect on specially configured clusters — inconsistent by design.

```sql
SHOW DATABASES;                          -- Hive Metastore's own top level
SELECT * FROM sales_db.orders LIMIT 5;   -- 2-level name: database.table
```

### Unity Catalog
A **governance layer** that does the metadata-catalog job Hive Metastore did — *and* adds a third
level (`catalog`), *and* takes over governing raw files too (via Volumes and External Locations,
replacing ungoverned DBFS access), *and* adds fine-grained GRANT/REVOKE, automatic lineage, and
centralized audit logs — shared across every workspace attached to the Metastore.

```sql
SHOW CATALOGS;                                    -- Unity Catalog's new top level
SELECT * FROM retail_sales.sales.orders LIMIT 5;  -- 3-level name: catalog.schema.table
```

## How They Relate (Not Just "Old vs New")

```
                     STORAGE (raw bytes)                  METADATA / GOVERNANCE
                     ────────────────────                 ──────────────────────
  DBFS          ──▶  Distributed filesystem over          (none — DBFS has no catalog
                     cloud storage. Mounted paths           or governance of its own)
                     like /dbfs/... or dbfs:/...
                     Ungoverned: any cluster user
                     can read/write any file.

  Hive          ──▶  Points at files on DBFS or a          Metadata catalog:
  Metastore          cloud path — doesn't manage             database.table names,
                     storage itself.                         columns, table-level ACLs
                                                               only, workspace-scoped,
                                                               no lineage.

  Unity         ──▶  GOVERNS storage directly:              Metadata catalog PLUS:
  Catalog            • Managed storage (auto-provisioned)     catalog.schema.table
                     • Volumes (governed files —               fine-grained GRANT/REVOKE
                       replaces raw DBFS access)                (catalog/schema/table/
                     • External Locations (governed              row/column)
                       external cloud paths)                    automatic lineage
                                                                  centralized audit logs
                                                                  account-wide, shared
                                                                  across every workspace
```

**Key insight:** Hive Metastore never governed DBFS — it just *pointed at* files sitting there,
ungoverned. Unity Catalog is the first layer that actually **governs both** the metadata *and*
the files underneath it, with one consistent rule set.

## Side-by-Side Comparison

| Aspect | DBFS | Hive Metastore | Unity Catalog |
|---|---|---|---|
| **What it is** | Distributed filesystem over cloud storage | Metadata catalog (table name → file location) | Unified governance for metadata + files + ML assets |
| **Solves** | "Where do bytes live, how do I read/write them?" | "What tables/databases exist, what are their columns?" | "Who can see/use what, tracked and audited, everywhere?" |
| **Scope** | Per workspace | Per workspace | Per account/region — shared across workspaces |
| **Namespace** | Flat file paths (`/mnt/...`) | 2-level: `database.table` | 3-level: `catalog.schema.table` |
| **Governs tables?** | No | Yes, basic ACLs | Yes, fine-grained (catalog/schema/table/row/column) |
| **Governs raw files?** | No — this *is* raw, ungoverned file access | No | Yes — Volumes and External Locations |
| **Access control** | None built-in; relies on cluster-level trust | Table ACLs, only enforced on specially configured clusters | SQL `GRANT`/`REVOKE`, enforced identically everywhere |
| **Lineage** | None | None | Automatic, table + column level |
| **Audit logging** | Minimal / cloud-provider only | Minimal / per-cluster | Centralized, queryable (`system.access.audit`) |
| **Example command** | `dbutils.fs.ls("/mnt/...")` | `SHOW DATABASES; SELECT * FROM db.table;` | `SHOW CATALOGS; SELECT * FROM cat.schema.table;` |
| **Status today** | Still exists; Databricks now recommends **Volumes** instead of the DBFS root for anything beyond temp/scratch files | Still exists; exposed read-only as the `hive_metastore` catalog for migration | Recommended path forward for everything |

## 5-Minute Hands-On: See All Three at Once

Run each of these in a notebook or SQL editor and compare the results:

```sql
-- 1. DBFS: raw file listing, no governance, no schema
%fs ls /databricks-datasets/

-- 2. Hive Metastore: the legacy, workspace-local metadata catalog
--    (still visible as a read-only catalog inside Unity Catalog)
SHOW DATABASES IN hive_metastore;
SHOW TABLES IN hive_metastore.default;

-- 3. Unity Catalog: the new, account-wide, governed catalog
SHOW CATALOGS;
SHOW SCHEMAS IN retail_sales;
SHOW TABLES IN retail_sales.sales;
SELECT * FROM retail_sales.sales.customers LIMIT 5;
```

**What to point out live:**
- Step 1 returns file paths — no permissions info, no schema, nothing SQL-aware.
- Step 2 returns `database.table` — two levels, no `catalog` in sight.
- Step 3 returns `catalog.schema.table` — three levels, and every object in it is protected by
  `GRANT`/`REVOKE`, tracked in lineage, and logged in the audit trail.

## Talking Points / Common Misconceptions

- **"Is Hive Metastore built on DBFS?"** Not necessarily — Hive Metastore just stores a *path*
  for each table, which is often on DBFS but could be any cloud path. They're independent layers
  that happened to be used together.
- **"Does Unity Catalog replace DBFS?"** It replaces the *governance gap* — you should stop
  putting production data straight on the DBFS root and use **Managed Tables** or **Volumes**
  instead. DBFS itself still exists underneath for workspace-local scratch/temp files.
- **"Why can Unity Catalog see `hive_metastore` as a catalog?"** So nothing breaks mid-migration —
  Unity Catalog wraps the legacy Hive Metastore as one more (read-only, ungoverned) catalog
  alongside your new, governed ones.

See also: `../diagrams/architecture_diagrams.md` (Diagrams 1–2 for the Hive Metastore vs Unity
Catalog picture) and `../platform_setup_demo/` for how Volumes/External Locations replace raw
DBFS access in practice.
