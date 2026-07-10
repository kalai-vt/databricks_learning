# PowerPoint Slide Content — Unity Catalog Demo

Source content for `UnityCatalog_Demo_Slides.pptx` (auto-generated from this file — see
`slides/build_pptx.py`). Each `##` heading is one slide: title + bullets.

## Unity Catalog for RetailCorp
- A hands-on Unity Catalog demo
- Presented as a 45-60 minute technical session
- Audience: SQL Developers, Data Engineers, BI Developers, Databricks beginners

## Agenda
- What is Unity Catalog & why it exists
- Hive Metastore vs Unity Catalog
- Architecture & components
- Live build: Catalogs, Schemas, Tables, Views
- Security: RBAC, GRANT/REVOKE, Access Denied
- External Tables, Volumes
- Data Lineage
- Recap & Q&A

## What is Unity Catalog?
- A unified governance layer for all data & AI assets
- Covers tables, views, volumes, ML models, functions
- One place to define access, track lineage, and audit usage
- Shared across every workspace attached to the same Metastore

## Why Unity Catalog Was Introduced
- Databricks scaled from a few notebooks to hundreds of workspaces
- Hive Metastore's per-workspace design could not govern at that scale
- No cross-workspace visibility, no lineage, no file governance
- Enterprises needed one governance plane, not many disconnected ones

## Problems with Legacy Hive Metastore
- Siloed: one metastore per workspace, no sharing
- Coarse, cluster-dependent table ACLs
- No built-in lineage tracking
- Raw files (DBFS mounts) were ungoverned
- Only a two-level namespace: database.table
- No native cross-account data sharing

## Hive Metastore vs Unity Catalog
- Scope: single workspace vs shared Metastore across workspaces
- Namespace: 2-level vs 3-level (catalog.schema.table)
- Permissions: cluster-dependent ACLs vs central SQL GRANT/REVOKE
- Lineage: none vs automatic, table & column level
- Files: ungoverned DBFS vs governed Volumes
- Sharing: copy/export vs Delta Sharing (no copy)

## Unity Catalog Architecture
- Metastore (one per cloud region)
- -> Catalog (per department / business unit / environment)
- -> Schema (grouping of related objects)
- -> Table / View / Volume / Function / Model
- Workspaces attach to a Metastore; many workspaces can share one

## Unity Catalog Components
- Metastore, Catalog, Schema
- Managed Table, External Table, View
- Volume, External Location, Storage Credential
- Function, Registered Model
- Share / Recipient / Provider (Delta Sharing)

## Metastore
- Top-level metadata container, one per region
- Stores catalogs, schemas, tables, grants, lineage
- Owns a default managed storage root
- Created once by an admin via Account Console

## Catalog
- First level of the three-level namespace
- Maps naturally to a department or business unit
- RetailCorp: retail_sales, retail_hr, retail_finance
- Primary boundary for broad access decisions

## Schema
- Second level: catalog.schema
- Groups related tables, views, volumes ("a folder")
- Every catalog auto-creates default and information_schema
- Example: retail_sales.sales, retail_hr.hr, retail_finance.finance

## Tables
- Structured, tabular data: catalog.schema.table
- Default format: Delta Lake (ACID, time travel)
- Two flavors: Managed and External
- Column-level comments power documentation & search

## Views
- A saved query, stores no data of its own
- Re-executed live against base tables on every query
- Governed with the same GRANT/REVOKE as tables
- Great for BI-facing models and hiding sensitive columns

## Volumes
- Govern access to non-tabular files (CSV, images, models)
- Live inside a schema, alongside tables
- Exposed at /Volumes/catalog/schema/volume/
- Managed or External, same pattern as tables

## External Locations
- Named, governed pointer: cloud path + storage credential
- Required before creating External Tables/Volumes outside managed storage
- Created and controlled by an admin

## Storage Credentials
- Cloud IAM role / service principal Unity Catalog can assume
- Decoupled from the specific storage path
- High-trust object — admin-only privilege to create

## Managed Tables
- No LOCATION clause -> Unity Catalog owns the storage path
- DROP TABLE deletes metadata AND data files
- Recommended default for most tables

## External Tables
- LOCATION clause points inside a registered External Location
- Unity Catalog manages metadata & permissions only
- DROP TABLE removes metadata only; files stay put
- Used when data must remain in a specific bucket

## Data Governance
- Centralized access control across every workspace
- Automatic lineage, tags, comments, classification
- Comprehensive, queryable audit logging
- One rule set enforced everywhere, every tool

## RBAC (Role-Based Access Control)
- Standard SQL GRANT / REVOKE statements
- Privileges: USE CATALOG, USE SCHEMA, SELECT, MODIFY, ALL PRIVILEGES
- ALL levels of the hierarchy must be satisfied to access an object
- Best practice: grant to groups, not individual users

## RetailCorp Security Demo
- Admin: full access, every catalog
- Sales User: retail_sales only, SELECT + MODIFY on orders/sales
- HR User: retail_hr only, ALL PRIVILEGES
- Finance User: retail_finance + read-only sales summary view
- Live demo: Access Denied errors proven in real time

## Data Lineage
- Captured automatically for every query, zero configuration
- Table-level AND column-level detail
- Visible in Catalog Explorer's Lineage tab
- Queryable via system.access.table_lineage

## RetailCorp Lineage Chain
- customers, orders, products, sales (tables)
- -> sales_summary_view (view)
- -> Power BI Dashboard (downstream, auto-captured)
- Enables impact analysis, audits, and root-cause debugging

## Sharing Data (Delta Sharing)
- Open protocol to share live data without copying it
- Create a SHARE, add objects, grant a RECIPIENT
- Works with Databricks and non-Databricks consumers
- No data duplication, no stale exports

## Catalog Explorer
- Point-and-click UI for the entire Unity Catalog object tree
- Browse, document, and tag catalogs/schemas/tables/volumes
- Grant/revoke permissions without writing SQL
- Explore interactive lineage graphs

## Recap
- One Metastore, one governance layer, every workspace
- Catalog -> Schema -> Table/View/Volume, three-level namespace
- RBAC enforced at every level, automatically
- Lineage tracked with zero developer effort
- RetailCorp: Sales, HR, and Finance cleanly isolated and governed

## Thank You / Q&A
- Full demo project: UnityCatalogDemo/ (notebooks, SQL, CSVs, docs)
- Interview questions: interview_questions/interview_questions.md
- Questions?
