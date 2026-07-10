# Architecture Diagrams (ASCII)

All diagrams are plain text — safe to paste into any slide, terminal, or chat during the demo.

---

## 1. Legacy Hive Metastore — Per-Workspace, Siloed

```
        Workspace A (Sales)             Workspace B (HR)             Workspace C (Finance)
      ┌───────────────────┐          ┌───────────────────┐        ┌───────────────────┐
      │  Hive Metastore A  │          │  Hive Metastore B  │        │  Hive Metastore C  │
      │  ─────────────────│          │  ─────────────────│        │  ─────────────────│
      │  db: sales_db      │          │  db: hr_db          │        │  db: finance_db     │
      │   ├─ customers     │          │   ├─ employees       │        │   ├─ ledger          │
      │   ├─ orders        │          │   └─ departments     │        │   └─ budget           │
      │   └─ ...           │          │                       │        │                       │
      └─────────┬──────────┘          └─────────┬──────────┘        └─────────┬──────────┘
                │                                │                              │
                ▼                                ▼                              ▼
      Permissions = cluster-level        Permissions = cluster-level    Permissions = cluster-level
      table ACLs (inconsistent,          table ACLs (inconsistent,      table ACLs (inconsistent,
      easy to bypass via file paths)     easy to bypass via file paths) easy to bypass via file paths)

      PROBLEMS:
      ✗ No sharing of metadata across workspaces — each is an island
      ✗ No central place to see "who can access what" across the company
      ✗ No cross-workspace lineage
      ✗ No governance for raw files (only tables) — DBFS mounts bypass ACLs entirely
      ✗ No fine-grained (column/row) security
      ✗ Auditing is manual, incomplete, per-cluster
```

---

## 2. Unity Catalog — One Governance Layer, Many Workspaces

```
                              ┌─────────────────────────────────────┐
                              │     UNITY CATALOG METASTORE          │
                              │     (one per cloud region)           │
                              │                                       │
                              │  Catalogs · Schemas · Tables · Views  │
                              │  Volumes · Grants · Lineage · Audit   │
                              └───────────────┬───────────────────────┘
                                              │  attached to
                  ┌───────────────────────────┼───────────────────────────┐
                  ▼                           ▼                           ▼
        Workspace A (Sales)         Workspace B (HR)             Workspace C (Finance)
      ┌───────────────────┐      ┌───────────────────┐        ┌───────────────────┐
      │  Compute clusters   │      │  Compute clusters   │        │  Compute clusters   │
      │  SQL Warehouses     │      │  SQL Warehouses     │        │  SQL Warehouses     │
      └───────────────────┘      └───────────────────┘        └───────────────────┘

      BENEFITS:
      ✓ ONE metadata + permissions layer shared by every workspace
      ✓ Grants defined once, enforced everywhere (notebooks, SQL, BI tools, jobs)
      ✓ Automatic lineage across workspaces and even across clouds
      ✓ Volumes govern raw files, not just tables
      ✓ Fine-grained security: catalog/schema/table/view/column/row level
      ✓ Centralized, queryable audit log (system.access.audit)
```

---

## 3. Object Hierarchy — Catalog → Schema → Table/View/Volume

```
                              METASTORE
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
  CATALOG                    CATALOG                    CATALOG
  retail_sales               retail_hr                  retail_finance
        │                         │                         │
        ▼                         ▼                         ▼
   SCHEMA                    SCHEMA                    SCHEMA
   sales                     hr                         finance
        │                         │                         │
   ┌────┼────┬────────┐     ┌────┴────┐               ┌────┴────┐
   ▼    ▼    ▼        ▼     ▼         ▼               ▼         ▼
customers products orders  VIEW   employees      departments  TABLE
   │    │    │   sales  sales_       │                │      finance_ledger
   │    │    │  (table) summary_     │                │      (EXTERNAL)
   │    │    │          view         │                │
   ▼    ▼    ▼                       ▼                ▼
 MANAGED MANAGED MANAGED          MANAGED          MANAGED
 TABLE   TABLE   TABLE            TABLE            TABLE

VOLUME:  retail_sales.sales.raw_files   (governed file storage, sibling of tables)

Fully-qualified name = catalog.schema.object   e.g.  retail_sales.sales.customers
```

---

## 4. Storage: Managed vs External

```
  MANAGED TABLE                              EXTERNAL TABLE
  ─────────────                              ──────────────
  CREATE TABLE customers (...);               CREATE TABLE finance_ledger (...)
  -- no LOCATION clause                       LOCATION 's3://retailcorp-finance-raw/ledger/'
        │                                            │
        ▼                                            ▼
  Unity Catalog CHOOSES the path           You SPECIFY the exact path
  under the Metastore/Catalog's                (must be inside a registered
  managed storage root:                          External Location)
        │                                            │
        ▼                                            ▼
  s3://retailcorp-uc-metastore-root/       s3://retailcorp-finance-raw/ledger/
    retail_sales/sales/customers/               (owned by an upstream SAP job,
                                                   NOT by Unity Catalog)
        │                                            │
        ▼                                            ▼
  DROP TABLE deletes METADATA              DROP TABLE deletes METADATA ONLY
  + DATA FILES (irreversible)              — data files are left untouched

  Storage Credential  ──▶  External Location  ──▶  External Table / External Volume
  (cloud IAM role)         (governed path + credential)   (points inside that path)
```

---

## 5. Users, Groups & Permissions (RBAC)

```
                         ACCOUNT-LEVEL IDENTITY
                    (Users & Groups, synced from IdP/SCIM)

     admin_user@..         sales_team (group)      hr_team (group)     finance_team (group)
          │                  │      │                    │                    │
          │           sales_user  (others)          hr_user              finance_user
          │                  │                            │                    │
          ▼                  ▼                            ▼                    ▼
  ┌───────────────┐   ┌─────────────────┐        ┌─────────────────┐  ┌───────────────────┐
  │ ALL PRIVILEGES │   │ USE CATALOG      │        │ USE CATALOG      │  │ USE CATALOG        │
  │ on every       │   │  retail_sales    │        │  retail_hr       │  │  retail_finance    │
  │ catalog        │   │ SELECT/MODIFY    │        │ ALL PRIVILEGES   │  │  + retail_sales     │
  │                │   │  on sales tables │        │  on hr schema    │  │ SELECT on           │
  │                │   │                  │        │                  │  │  sales_summary_view │
  └───────────────┘   └─────────────────┘        └─────────────────┘  └───────────────────┘
                              │                            │                    │
                              ▼                            ▼                    ▼
                        retail_sales                 retail_hr            retail_finance
                        (✓ allowed)                  (✗ Access Denied     (✓ allowed, view only)
                                                       for sales_user)     retail_sales base tables
                                                                            (✗ Access Denied)

  RULE: USE CATALOG *and* USE SCHEMA *and* SELECT/MODIFY on the object are ALL required.
        Missing any one link in the chain = Access Denied.
```

---

## 6. Lineage Graph

```
  retail_sales.sales.customers  ─┐
  retail_sales.sales.orders    ──┼──▶  retail_sales.sales.sales_summary_view  ──▶  Power BI Dashboard
  retail_sales.sales.products  ──┤            (VIEW — Notebook 6)                  (downstream, auto-captured)
  retail_sales.sales.sales     ──┘

  Captured automatically by Unity Catalog for every query, at TABLE level and COLUMN level.
  Visible in Catalog Explorer → object → "Lineage" tab, or queryable via
  system.access.table_lineage / system.access.column_lineage.
```
