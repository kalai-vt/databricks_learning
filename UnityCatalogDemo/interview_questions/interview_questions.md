# Interview Questions — Unity Catalog

Organized to match the 21 concept sections in `docs/01_concepts_overview.md`. Use these to close
out each topic during the demo, or as standalone interview prep.

## 1. What is Unity Catalog?
**Q: What is Unity Catalog in one sentence?**
A: A unified, centralized governance layer for all data and AI assets (tables, views, volumes,
ML models, files) across every Databricks workspace attached to it.

**Q: What problem does Unity Catalog solve that a single workspace's built-in metastore didn't?**
A: Cross-workspace governance — one place to define catalogs, permissions, lineage, and audit
logs instead of duplicating/reconciling them per workspace.

## 2. Why Unity Catalog was introduced?
**Q: Why did Databricks introduce Unity Catalog instead of extending Hive Metastore?**
A: Hive Metastore's design (one metastore per workspace/cluster, coarse table-only ACLs, no
lineage, no file governance) couldn't scale to enterprise governance needs — it needed a
ground-up redesign, not a patch.

## 3. Problems with Legacy Hive Metastore
**Q: Name three limitations of the legacy Hive Metastore.**
A: (1) Siloed per workspace — no cross-workspace metadata sharing. (2) Coarse, inconsistent
table-level ACLs enforced differently per cluster. (3) No native lineage, no governance over raw
files/volumes, and only a two-level namespace (database.table).

## 4. Difference between Hive Metastore and Unity Catalog
**Q: What is the fundamental architectural difference?**
A: Hive Metastore is scoped to one workspace with a two-level namespace (`database.table`); Unity
Catalog is scoped to a region-wide Metastore shared across workspaces with a three-level namespace
(`catalog.schema.table`), plus built-in lineage, audit, and file governance via Volumes.

**Q: Can the two coexist?**
A: Yes — Unity Catalog exposes the legacy Hive Metastore as a read-only catalog named
`hive_metastore` for backward compatibility during migration.

## 5. Unity Catalog Architecture
**Q: Describe the Unity Catalog object hierarchy top to bottom.**
A: Metastore → Catalog → Schema → Table/View/Volume/Function/Model.

**Q: How does a workspace relate to a Metastore?**
A: A workspace is *attached* to exactly one Metastore (per region); a Metastore can be attached to
many workspaces.

## 6. Unity Catalog Components
**Q: List the main securable object types in Unity Catalog.**
A: Metastore, Catalog, Schema, Table (managed/external), View, Volume, External Location, Storage
Credential, Function, Registered Model, Share, Recipient, Provider.

## 7. Metastore
**Q: What does a Metastore actually store?**
A: Metadata (definitions, comments, tags, lineage, grants) for every catalog underneath it, plus
a pointer to its default managed storage root.

**Q: How many Metastores does a typical enterprise account have?**
A: Usually one per cloud region the organization operates in.

## 8. Catalog
**Q: What is a Catalog used for in practice?**
A: The top-level grouping for a business unit, department, or environment (e.g. `dev`/`prod`) —
in our demo, one catalog per department (`retail_sales`, `retail_hr`, `retail_finance`).

**Q: What SQL command lists all catalogs in the current Metastore?**
A: `SHOW CATALOGS;`

## 9. Schema
**Q: What is a Schema, and what's another name for it?**
A: A Schema (a.k.a. database) groups related tables/views/volumes inside a catalog — the second
level of the three-level namespace.

**Q: What two schemas exist automatically in every new catalog?**
A: `default` and `information_schema`.

## 10. Tables
**Q: What is the default table format in Unity Catalog?**
A: Delta Lake.

**Q: How do you check whether a table is Managed or External?**
A: `DESCRIBE TABLE EXTENDED <table>` and check the `Type` field.

## 11. Views
**Q: Do Views store their own data?**
A: No — a view stores only a saved query; it's re-executed against the underlying tables every
time it's queried.

**Q: Give one governance reason to use a view instead of granting access to the base table.**
A: Column-level exposure control — e.g. `employee_department_view` omits `salary`/`email` so a
broad grant on the view never leaks compensation data.

## 12. Volumes
**Q: What problem do Volumes solve that Tables don't?**
A: Governance (GRANT/REVOKE, audit) for non-tabular files — CSVs, images, model artifacts —
which previously lived in ungoverned DBFS mounts.

**Q: What are the two types of Volumes?**
A: Managed Volumes (Unity Catalog owns the storage path) and External Volumes (point at a path
inside a registered External Location).

## 13. External Locations
**Q: What does an External Location represent?**
A: A governed pointer combining a cloud storage path with a Storage Credential, explicitly
authorizing Unity Catalog to read/write that path.

**Q: Who typically creates External Locations?**
A: A Metastore/cloud admin — it requires the `CREATE EXTERNAL LOCATION` privilege because it
grants access to real cloud storage.

## 14. Storage Credentials
**Q: What is a Storage Credential?**
A: A cloud IAM role or service principal that Unity Catalog is trusted to assume in order to
access a cloud storage account — the credential itself, decoupled from any specific path.

**Q: Why are Storage Credentials and External Locations separated as two objects?**
A: Separation of concerns/least privilege — a credential can back multiple external locations,
and access to a *path* can be granted without exposing the underlying credential directly.

## 15. Managed Tables
**Q: What happens to the data when you `DROP` a Managed Table?**
A: Both the metadata *and* the underlying data files are deleted — irreversible.

**Q: Do you need to specify a storage path when creating a Managed Table?**
A: No — Unity Catalog automatically chooses one under the catalog/schema's managed storage root.

## 16. External Tables
**Q: What happens to the data when you `DROP` an External Table?**
A: Only the Unity Catalog metadata is removed; the underlying files remain untouched in cloud
storage.

**Q: When would you choose an External Table over a Managed Table?**
A: When the data must stay in a specific bucket/path for compliance, cost allocation, or
integration with tools outside Databricks (e.g. an upstream SAP export job).

## 17. Data Governance
**Q: What does "governance" mean concretely in Unity Catalog?**
A: Centrally defining who can see/modify what data, tracking where data came from and where it
flows (lineage), and auditing every access — all enforced consistently regardless of which tool
or workspace is used.

## 18. RBAC
**Q: What privilege levels are commonly used, from broadest to narrowest read/write?**
A: `ALL PRIVILEGES` > `MODIFY` (includes write) > `SELECT` (read-only), plus container-level
`USE CATALOG`/`USE SCHEMA` gates that must also be granted.

**Q: Why grant to groups instead of individual users?**
A: Onboarding/offboarding becomes a group-membership change instead of hunting down every
individual GRANT — much lower operational risk.

## 19. Data Lineage
**Q: How does Unity Catalog capture lineage — do you have to configure it?**
A: Automatically, by analyzing the query plan of every statement that reads/writes a governed
object. No manual tagging required.

**Q: Where can you view lineage besides the UI?**
A: Query the `system.access.table_lineage` and `system.access.column_lineage` system tables.

## 20. Sharing Data
**Q: What Unity Catalog feature lets you share data with another organization without copying it?**
A: Delta Sharing — an open protocol; you create a `SHARE`, add objects to it, and grant a
`RECIPIENT` (which may be another Databricks account or a non-Databricks client) access.

**Q: Does the data consumer need to be on Databricks to receive a Delta Share?**
A: No — Delta Sharing is an open, cross-platform protocol; recipients can use pandas, Spark,
Power BI, or any Delta Sharing connector.

## 21. Catalog Explorer
**Q: What is Catalog Explorer?**
A: The Databricks UI for browsing catalogs/schemas/tables/volumes, viewing/editing permissions,
reading documentation and tags, and exploring lineage graphs — all without writing SQL.

**Q: Name two things you can do in Catalog Explorer that you'd otherwise need multiple SQL
statements for.**
A: Grant/revoke permissions via a checkbox UI, and visually explore a lineage graph interactively.

---

## Cross-Cutting / "Gotcha" Questions

**Q: If a user has `SELECT` on a table but not `USE CATALOG` on its catalog, can they query it?**
A: No — every level of the hierarchy (`USE CATALOG`, `USE SCHEMA`, object-level privilege) is
checked independently; all must be satisfied.

**Q: Does granting `SELECT` on a view also grant `SELECT` on its underlying base tables?**
A: No. View access and base table access are independent grants — a common design pattern
specifically to expose derived/aggregated data without exposing raw tables.

**Q: What is the three-level namespace, and why does it matter?**
A: `catalog.schema.table` — it removes ambiguity when the same schema/table name is reused across
departments or environments, and is the foundation that makes cross-catalog joins and per-catalog
governance possible.

**Q: Is Unity Catalog cloud-specific?**
A: No — it works consistently across AWS, Azure, and GCP Databricks deployments, which is part of
its value proposition for multi-cloud organizations.

**Q: What's the difference between DBFS, Hive Metastore, and Unity Catalog?**
A: DBFS is a storage layer — a distributed filesystem over cloud storage, for reading/writing raw
files with no schema or access control. Hive Metastore is a metadata layer — a catalog mapping
`database.table` names to file locations (often on DBFS), with only basic, cluster-dependent table
ACLs. Unity Catalog is a governance layer — it does the metadata-catalog job (with a third
`catalog` level added) *and* governs the files themselves (via Volumes/External Locations,
replacing ungoverned DBFS access), plus adds fine-grained GRANT/REVOKE, lineage, and audit logs,
shared across every workspace. See `../docs/03_dbfs_vs_hive_metastore_vs_unity_catalog.md`.

**Q: Did Hive Metastore govern the files stored on DBFS?**
A: No. Hive Metastore only stored a *pointer* (path) to where a table's data lived; it never
controlled who could read/write the underlying files directly on DBFS. That ungoverned gap is
exactly what Unity Catalog Volumes and External Locations close.
