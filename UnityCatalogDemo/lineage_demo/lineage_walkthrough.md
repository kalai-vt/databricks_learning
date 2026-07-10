# Data Lineage Demo

## The Chain

```
retail_sales.sales.customers ─┐
retail_sales.sales.orders ────┼──▶ retail_sales.sales.sales_summary_view ──▶ Power BI Dashboard
retail_sales.sales.products ──┤            (Notebook 6 / sql_scripts/05)         (Notebook 12)
retail_sales.sales.sales ─────┘
```

In plain English: four base tables owned by the Sales department are joined into one view;
that view is then consumed by a Power BI dashboard that the CFO looks at every Monday morning.

## Why This Matters (the pitch to a beginner audience)

Before Unity Catalog, answering *"where did this number in the dashboard come from, and what
happens if I change the `orders` table schema?"* meant manually reading code, asking around, or
maintaining a separate lineage tool. Unity Catalog answers both questions **automatically**,
because it parses the query plan of every statement that touches a governed table or view.

## How Unity Catalog Captures Lineage

1. Every time a SQL statement, notebook cell, Job, or DLT/Lakeflow pipeline **reads or writes** a
   Unity-Catalog-governed table, view, or volume, the query's logical plan is analyzed.
2. Unity Catalog records: which objects were read (**upstream**), which object was written
   (**downstream**), at the **table level** and the **column level**, plus who ran it and when.
3. This is captured centrally in the Metastore — visible from **every workspace** attached to
   that Metastore, not just the one where the query ran.
4. External consumers (Power BI, Tableau, any JDBC/ODBC client) are captured too: the moment they
   run a `SELECT` against a governed view via a Databricks SQL Warehouse connection, that
   connection shows up as a downstream lineage node.

## Where to See It

### 1. Catalog Explorer (visual, best for a live demo)
```
Catalog Explorer → retail_sales → sales → sales_summary_view → "Lineage" tab
```
- **Table tab**: shows the 4 upstream tables and any downstream consumers as a graph you can
  click through in both directions.
- **Column tab**: shows column-level lineage, e.g. `sales_summary_view.amount` ← `sales.amount`.

### 2. System Tables (programmatic, for building custom governance dashboards)
```sql
SELECT source_table_full_name, target_table_full_name, source_type, target_type, event_time
FROM system.access.table_lineage
WHERE target_table_full_name = 'retail_sales.sales.sales_summary_view'
ORDER BY event_time DESC;
```
Also available: `system.access.column_lineage` for column-level detail.

## Connecting the Downstream Node: Power BI

1. Power BI Desktop → **Get Data → Databricks** → enter the SQL Warehouse hostname & HTTP path.
2. Browse to `retail_sales → sales → sales_summary_view`, load it as a dataset.
3. Build a simple bar chart: revenue by `category`, or a line chart: revenue by `order_date`.
4. Publish. Back in Catalog Explorer, refresh the lineage graph on `sales_summary_view` — the
   Power BI dataset now appears as a downstream node, **captured automatically**, no manual
   tagging required.

## Business Value Talking Points

- **Impact analysis**: "If I drop the `region` column from `sales`, what breaks downstream?"
  Lineage answers this before you make the change, not after a dashboard turns red in production.
- **Audit & compliance**: "Prove where this revenue figure in the board deck came from." Lineage
  is the paper trail — from raw table, through every transformation, to the exact dashboard.
- **Onboarding**: new team members can visually explore how data flows through the company
  instead of reading tribal-knowledge documentation that's usually out of date.
- **Root-cause debugging**: a wrong number in a dashboard can be traced backward through the
  graph to the exact upstream table/column that introduced the error.
