# Business Scenario — RetailCorp

## The Company

**RetailCorp** is a mid-sized retail company selling electronics, apparel, footwear, and home
goods across India. Like most growing companies, it has three departments that each own their own
data and don't want (or aren't allowed) to see each other's:

| Department | Owns | Sensitive? |
|---|---|---|
| **Sales** | Customers, products, orders, sales transactions | Customer PII (email) |
| **HR** | Employees, departments | Salary, employee PII |
| **Finance** | Revenue/ledger data (sourced from an external SAP export) | Financial data |

## Why Unity Catalog Fits

- Each department gets its **own Catalog** (`retail_sales`, `retail_hr`, `retail_finance`) —
  clean, obvious data ownership boundaries that map directly to how the business is organized.
- **RBAC** enforces that Sales reps never see salaries, HR never sees customer PII, and Finance
  only sees the sales numbers it actually needs (via a curated view, not raw tables).
- **Lineage** lets the Finance team's Power BI dashboard prove exactly where its revenue numbers
  came from — important the first time an auditor asks.
- **External Tables** model the reality that Finance's ledger data is produced by an external SAP
  export job and must stay in its own bucket — Unity Catalog governs it without taking it over.
- **Volumes** give Sales a governed landing zone for the raw CSV exports it receives before they're
  loaded into managed Delta tables.

## Data Model Used in This Demo

```
retail_sales (catalog)
  └── sales (schema)
        ├── customers          (managed table, 20 rows)
        ├── products            (managed table, 20 rows)
        ├── orders               (managed table, 20 rows)
        ├── sales                 (managed table, 20 rows — fact table)
        ├── sales_summary_view     (view: join of the 4 tables above)
        └── raw_files               (volume: CSV landing zone)

retail_hr (catalog)
  └── hr (schema)
        ├── departments          (managed table, 6 rows)
        ├── employees             (managed table, 20 rows)
        └── employee_department_view (view: excludes salary/email)

retail_finance (catalog)
  └── finance (schema)
        └── finance_ledger        (external table, points at s3://retailcorp-finance-raw/ledger/)
```

## Entity Relationships

```
customers (1) ──< (many) orders (many) >── (1) products
                        │
                        │ 1:1
                        ▼
                      sales  (transaction amount, region, channel)

departments (1) ──< (many) employees
```

This is intentionally simple — realistic enough to carry every Unity Catalog concept in the
syllabus, small enough to build and query live within a one-hour session.
