# 25 & 26 — Introduction to Unity Catalog + Object Model (~5 min)

## 25. What is Unity Catalog? (one breath)

Unity Catalog is a **single, account-level governance layer** for all data and AI assets —
tables, views, volumes, ML models — shared across every workspace in your Databricks account.
Before it existed, each workspace had its own private Hive Metastore with no shared visibility,
no shared permissions, and no shared lineage.

## 26. Object Model: Hive Metastore vs Unity Catalog

```
HIVE METASTORE (legacy)                     UNITY CATALOG
────────────────────────                    ─────────────
Scope: ONE per workspace                    Scope: ONE per account (region), shared by
                                             many workspaces

  Workspace                                    ACCOUNT
     │                                            │
     ▼                                            ▼
  Hive Metastore                              METASTORE  (created once, admin only)
     │                                            │
     ▼                                 ┌──────────┼──────────┐
  database                             ▼          ▼          ▼
     │                              Workspace A  Workspace B  Workspace C
     ▼                              (attached)   (attached)   (attached)
   table                                          │
                                                   ▼
  2-level namespace:                          CATALOG   (new top level!)
  database.table                                  │
                                                   ▼
                                               SCHEMA
                                                   │
                                                   ▼
                                         TABLE / VIEW / VOLUME / MODEL

                                          3-level namespace:
                                          catalog.schema.table
```

**Key differences to call out live:**
- Hive Metastore = **workspace-scoped**. Unity Catalog Metastore = **account-scoped**, attached to
  many workspaces at once.
- Hive Metastore = **2-level** name (`database.table`). Unity Catalog = **3-level** name
  (`catalog.schema.table`) — the extra `catalog` level is what lets one Metastore cleanly host
  many departments/teams.
- Unity Catalog also governs **files** (Volumes), **ML models**, and tracks **lineage** —
  none of which Hive Metastore ever did.
- Both can coexist: Unity Catalog exposes the workspace's old Hive Metastore as a read-only
  catalog literally named `hive_metastore`, so nothing breaks during migration.

**Quick hands-on check (run in any notebook/SQL editor):**
```sql
SHOW CATALOGS;
-- hive_metastore is listed right alongside your new Unity Catalog catalogs
```
