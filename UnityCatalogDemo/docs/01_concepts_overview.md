# Unity Catalog — Concepts Overview

A reference companion to the live demo. Read top to bottom for the full story, or jump to a
numbered section that matches the notebook/topic you're on.

## 1. What is Unity Catalog?

Unity Catalog is Databricks' **unified governance solution** for all data and AI assets — tables,
views, volumes (files), ML models, and functions — across every workspace attached to it. It
provides one place to define **who can access what**, **track where data came from**, and
**audit every access**, consistently, regardless of which workspace, cluster, SQL Warehouse, or
BI tool is being used.

## 2. Why Unity Catalog was introduced

As Databricks customers grew from a handful of notebooks to hundreds of workspaces, thousands of
tables, and multiple business units, the workspace-scoped Hive Metastore model broke down:
permissions had to be re-created per workspace, there was no cross-workspace visibility, and
compliance teams had no reliable way to answer "who accessed this data, and where did it come
from." Unity Catalog was built to be the single governance plane an enterprise actually needs.

## 3. Problems with Legacy Hive Metastore

- **Siloed per workspace** — a table created in one workspace's metastore is invisible to another.
- **Coarse permissions** — typically table-level only, enforced inconsistently depending on
  cluster configuration (table ACLs required a specific cluster mode to even be enforced).
- **No lineage** — no built-in way to trace how data flowed from raw ingestion to a dashboard.
- **No governance for files** — raw files accessed via DBFS mounts bypassed table ACLs entirely.
- **Two-level namespace only** — `database.table`, no higher-level grouping like a catalog.
- **No native cross-cloud/cross-account sharing** — sharing data externally required exporting or
  duplicating it.

## 4. Difference between Hive Metastore and Unity Catalog

| Aspect | Hive Metastore (Legacy) | Unity Catalog |
|---|---|---|
| Scope | Single workspace | Shared across many workspaces (region-wide Metastore) |
| Namespace | 2-level: `database.table` | 3-level: `catalog.schema.table` |
| Permission model | Table ACLs, cluster-dependent, inconsistent | Central SQL GRANT/REVOKE, enforced everywhere |
| Fine-grained security | Limited | Catalog/schema/table/view/row/column level |
| Lineage | None built-in | Automatic, table & column level |
| File governance | None (raw DBFS mounts) | Volumes |
| External data | Manual/ungoverned mounts | Storage Credentials + External Locations (governed) |
| Data sharing | Export/copy data | Delta Sharing (open protocol, no copy) |
| Auditing | Manual/per-cluster | Centralized, queryable system tables |
| Multi-cloud consistency | Varies | Consistent across AWS/Azure/GCP |

## 5. Unity Catalog Architecture

```
Metastore (1 per region)
   └── Catalog (per department/business unit/environment)
         └── Schema (grouping of related objects)
               ├── Table (Managed or External)
               ├── View
               ├── Volume (governed files)
               ├── Function
               └── Registered Model
```
A Metastore is created once (by an admin, via Account Console) and workspaces are attached to it.
See `diagrams/architecture_diagrams.md` for the full ASCII picture.

## 6. Unity Catalog Components

Metastore, Catalog, Schema, Managed Table, External Table, View, Volume, External Location,
Storage Credential, Function, Registered Model (MLflow), Share/Recipient/Provider (Delta Sharing),
and the enforcement + audit layer (Grants, Lineage, System Tables) that ties them together.

## 7. Metastore

The top-level container for all metadata in a region. Stores catalog/schema/table definitions,
comments, tags, grants, and lineage. Owns a default managed storage root. Created and assigned to
workspaces by an account admin — not created via SQL.

## 8. Catalog

The first level of the three-level namespace. In this demo: `retail_sales`, `retail_hr`,
`retail_finance` — one per department. Catalogs are the primary boundary for broad access
decisions ("Finance can't see HR at all").

## 9. Schema

The second level (`catalog.schema`), a.k.a. database. Groups related tables/views/volumes. Every
new catalog automatically gets a `default` schema and a read-only `information_schema`.

## 10. Tables

The structured, tabular data objects (`catalog.schema.table`). Default format is Delta Lake, which
gives ACID transactions, time travel (`DESCRIBE HISTORY`), and automatic optimization. Can be
**Managed** or **External** (see 15/16 below).

## 11. Views

A saved query, no data of its own, re-executed live on each query. Governed with the same
GRANT/REVOKE model as tables. Commonly used to simplify BI-facing data models and to expose a safe
subset of columns.

## 12. Volumes

Unity Catalog objects that govern access to **non-tabular files** (CSV, JSON, images, model
checkpoints). Live in a Schema alongside tables (`catalog.schema.volume`). Managed or External,
mirroring the Managed/External Table distinction. Exposed at a filesystem path:
`/Volumes/catalog/schema/volume/`.

## 13. External Locations

A named, governable combination of a **cloud storage path** + a **Storage Credential**,
explicitly authorizing Unity Catalog to read/write that path. Required before creating any
External Table or External Volume outside the Metastore's own managed storage.

## 14. Storage Credentials

A cloud IAM role / service principal that Unity Catalog is trusted to assume to access a specific
cloud storage account. The credential is separate from the path (External Location) that uses it
— separation of concerns, least privilege.

## 15. Managed Tables

Created **without** a `LOCATION` clause. Unity Catalog chooses the storage path (under the
catalog/schema's managed root) and fully owns the data lifecycle. `DROP TABLE` deletes metadata
**and** data files. Recommended default for most tables.

## 16. External Tables

Created **with** a `LOCATION` clause pointing inside a registered External Location. Unity
Catalog manages metadata and permissions only; the files stay exactly where they are. `DROP TABLE`
removes metadata only — data is untouched. Used when data must remain in a specific bucket for
compliance or integration reasons.

## 17. Data Governance

The overall practice Unity Catalog enables: centrally defined access control, automatic lineage,
comprehensive audit logging, data classification via tags/comments, and (with add-ons like
Attribute-Based Access Control) fine-grained row/column security — all enforced identically no
matter which workspace, tool, or user connects.

## 18. RBAC (Role-Based Access Control)

Standard SQL `GRANT`/`REVOKE` statements assign privileges (`USE CATALOG`, `USE SCHEMA`, `SELECT`,
`MODIFY`, `ALL PRIVILEGES`, `CREATE TABLE`, etc.) to principals (users or, preferably, groups).
Privileges must be satisfied at **every** level of the object hierarchy simultaneously — see
`security_demo/` for the full grant matrix and access-denied demo.

## 19. Data Lineage

Automatically captured table- and column-level lineage for every query that touches a governed
object — no manual tagging. Viewable in Catalog Explorer's Lineage tab or queried via
`system.access.table_lineage` / `system.access.column_lineage`. See `lineage_demo/` for the full
walkthrough.

## 20. Sharing Data

**Delta Sharing** is Unity Catalog's open protocol for sharing live data with other
organizations — or other Databricks accounts — **without copying it**. You create a `SHARE`,
add tables/views/volumes to it, and grant access to a `RECIPIENT`. Recipients can be Databricks
accounts (Databricks-to-Databricks sharing) or any Delta Sharing-compatible client (pandas, Spark,
Power BI) for open sharing.

## 21. Catalog Explorer

The point-and-click UI for Unity Catalog: browse the catalog/schema/table/volume tree, read and
edit documentation/comments/tags, grant/revoke permissions with a checkbox UI, preview sample
data, and explore interactive lineage graphs — all without writing SQL. The natural home for a
non-technical stakeholder to self-serve discovery.
