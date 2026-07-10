-- =====================================================================
-- 05_create_view.sql
-- Purpose : CREATE VIEW statements
-- =====================================================================

USE CATALOG retail_sales;
USE SCHEMA sales;

CREATE OR REPLACE VIEW sales_summary_view
COMMENT 'One row per order: customer, product and sale amount — feeds the Power BI revenue dashboard'
AS
SELECT
  o.order_id,
  c.customer_id,
  c.customer_name,
  c.state,
  p.product_id,
  p.product_name,
  p.category,
  o.order_date,
  o.quantity,
  s.amount,
  s.region,
  s.channel
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products  p ON o.product_id  = p.product_id
JOIN sales     s ON s.order_id    = o.order_id
WHERE o.order_status = 'Delivered';

USE CATALOG retail_hr;
USE SCHEMA hr;

CREATE OR REPLACE VIEW employee_department_view
COMMENT 'Employee directory without sensitive salary/email columns'
AS
SELECT
  e.employee_id,
  e.employee_name,
  e.job_title,
  e.hire_date,
  d.department_name,
  d.location,
  d.manager_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

SELECT * FROM retail_sales.sales.sales_summary_view LIMIT 10;
SELECT * FROM retail_hr.hr.employee_department_view LIMIT 10;
