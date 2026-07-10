# Security & RBAC Demo — Grant Matrix

## Personas

| Persona | Principal (demo) | Role in company |
|---|---|---|
| **Admin** | `admin_user@retailcorp.com` | Platform/Metastore admin, full control everywhere |
| **Sales User** | `sales_user@retailcorp.com` (group `sales_team`) | Sales rep — reads/writes sales data |
| **HR User** | `hr_user@retailcorp.com` (group `hr_team`) | HR staff — full access to HR data only |
| **Finance User** | `finance_user@retailcorp.com` (group `finance_team`) | Finance analyst — reads finance ledger + sales revenue view |

## Grant Matrix

| Object | Admin | Sales User | HR User | Finance User |
|---|:---:|:---:|:---:|:---:|
| `retail_sales` catalog (`USE CATALOG`) | ALL | ✅ | ❌ | ✅ |
| `retail_sales.sales.customers` | ALL | SELECT | ❌ | ❌ |
| `retail_sales.sales.products` | ALL | SELECT | ❌ | ❌ |
| `retail_sales.sales.orders` | ALL | SELECT, MODIFY | ❌ | ❌ |
| `retail_sales.sales.sales` | ALL | SELECT, MODIFY | ❌ | ❌ |
| `retail_sales.sales.sales_summary_view` | ALL | SELECT | ❌ | SELECT |
| `retail_hr` catalog (`USE CATALOG`) | ALL | ❌ | ✅ | ❌ |
| `retail_hr.hr.employees` (incl. `salary`) | ALL | ❌ | ALL PRIVILEGES | ❌ |
| `retail_hr.hr.departments` | ALL | ❌ | ALL PRIVILEGES | ❌ |
| `retail_hr.hr.employee_department_view` | ALL | ❌ | ALL PRIVILEGES | ❌ |
| `retail_finance` catalog (`USE CATALOG`) | ALL | ❌ | ❌ | ✅ |
| `retail_finance.finance.finance_ledger` | ALL | ❌ | ❌ | SELECT |

**Legend:** ALL = `ALL PRIVILEGES`, ✅ = `USE CATALOG`/`USE SCHEMA` granted, ❌ = no grant (blocked).

## Design Principles Demonstrated

1. **Least privilege** — Sales gets `MODIFY` only on the two tables it actually writes
   (`orders`, `sales`); `customers`/`products` stay `SELECT`-only for Sales.
2. **Department isolation** — HR data is completely invisible to Sales and Finance; Sales
   transactional tables are invisible to HR. Two independent, non-overlapping blast radii.
3. **Cross-functional read access done narrowly** — Finance needs revenue numbers, so it gets
   `SELECT` on exactly one **view** (`sales_summary_view`), not the underlying `orders`/`sales`
   tables, and not `customers`/`products`.
4. **PII protection by view design** — `employee_department_view` simply omits `salary` and
   `email`, so even a principal with broad HR access via the view (not the base table) never sees
   compensation data.
5. **Group-based grants** (see `01_setup_users_groups.sql`) — grants target `sales_team`,
   `hr_team`, `finance_team`, not individual emails, so onboarding/offboarding is a group
   membership change, not a GRANT/REVOKE hunt.

## Live Demo Script (5 minutes)

1. As **Admin**, run `sql_scripts/06_grant.sql` to apply the matrix above.
2. Switch to the **Sales User** identity (or open a second browser profile logged in as
   `sales_user@retailcorp.com`) and run:
   ```sql
   SELECT * FROM retail_sales.sales.customers LIMIT 5;      -- ✅ works
   SELECT * FROM retail_hr.hr.employees LIMIT 5;             -- ❌ Access Denied
   ```
3. Switch to the **HR User** identity and run:
   ```sql
   SELECT * FROM retail_hr.hr.employees LIMIT 5;             -- ✅ works, sees salary
   SELECT * FROM retail_sales.sales.orders LIMIT 5;          -- ❌ Access Denied
   ```
4. Switch to the **Finance User** identity and run:
   ```sql
   SELECT * FROM retail_sales.sales.sales_summary_view LIMIT 5;  -- ✅ works (view only)
   SELECT * FROM retail_sales.sales.orders LIMIT 5;               -- ❌ Access Denied (base table)
   SELECT * FROM retail_hr.hr.employees LIMIT 5;                  -- ❌ Access Denied
   ```
5. Point out the exact error text (see `03_access_denied_demo.sql`) and explain it's enforced
   **identically** whether the query comes from a notebook, Databricks SQL editor, or an external
   BI tool connected via ODBC/JDBC — one governance layer, everywhere.
