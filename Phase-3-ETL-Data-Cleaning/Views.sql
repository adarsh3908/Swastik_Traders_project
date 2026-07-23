-- ============================================================
-- Swastik Traders — Analytical Views
-- Phase 2: Database Design
-- Version: 1.0  |  Date: July 2026
-- ============================================================

USE swastik_traders_clean;

-- ── 1. vw_sales_detailed ──────────────────────────────────
-- Combines header and line item sales data with customer, product, category, brand,
-- employee, and promotion details.
-- Primary use: Sales trends, product performance, employee billing performance, promotion impact.
DROP VIEW IF EXISTS vw_sales_detailed;
CREATE VIEW vw_sales_detailed AS
SELECT
    s.sale_id,
    s.sale_date,
    s.payment_method,
    s.payment_status,
    si.sale_item_id,
    si.quantity,
    si.unit_price,
    si.cost_price,
    si.discount_pct,
    si.profit_amount,
    -- Net revenue after discount
    ROUND(si.quantity * si.unit_price * (1 - si.discount_pct / 100.0), 2) AS net_revenue,
    -- Customer info
    c.customer_id,
    c.name AS customer_name,
    c.customer_type,
    c.area AS customer_area,
    -- Product info
    p.product_id,
    p.product_name,
    p.color AS product_color,
    p.pack_size,
    p.unit,
    -- Category info
    pc.category_id,
    pc.category_name,
    parent_pc.category_name AS parent_category_name,
    -- Brand info
    b.brand_id,
    b.brand_name,
    -- Warehouse info
    w.warehouse_id,
    w.warehouse_name,
    -- Employee info
    e.employee_id,
    e.name AS employee_name,
    e.role AS employee_role,
    -- Promotion info
    promo.promotion_id,
    promo.promo_name,
    promo.promo_type,
    promo.discount_pct AS promo_discount_pct
FROM
    sales s
    JOIN sales_items si            ON s.sale_id = si.sale_id
    JOIN customers c               ON s.customer_id = c.customer_id
    JOIN products p                ON si.product_id = p.product_id
    JOIN product_categories pc     ON p.category_id = pc.category_id
    LEFT JOIN product_categories parent_pc ON pc.parent_category_id = parent_pc.category_id
    JOIN brands b                  ON p.brand_id = b.brand_id
    JOIN warehouses w              ON si.warehouse_id = w.warehouse_id
    JOIN employees e               ON s.employee_id = e.employee_id
    LEFT JOIN promotions promo     ON s.promotion_id = promo.promotion_id;


-- ── 2. vw_inventory_status ────────────────────────────────
-- Shows current inventory levels per warehouse, reorder alerts, and dead stock indicators.
-- Primary use: Stock replenishment, warehouse space check, dead stock valuation.
DROP VIEW IF EXISTS vw_inventory_status;
CREATE VIEW vw_inventory_status AS
SELECT
    i.inventory_id,
    i.quantity_in_stock,
    i.reorder_level,
    i.dead_stock_flag,
    i.last_updated,
    -- Reorder alert
    CASE 
        WHEN i.quantity_in_stock <= i.reorder_level THEN 'Reorder Alert'
        ELSE 'Stock OK'
    END AS stock_status,
    -- Product info
    p.product_id,
    p.product_name,
    p.color AS product_color,
    p.pack_size,
    p.unit,
    p.cost_price,
    p.selling_price,
    -- Inventory value
    ROUND(i.quantity_in_stock * p.cost_price, 2) AS stock_value_at_cost,
    ROUND(i.quantity_in_stock * p.selling_price, 2) AS stock_value_at_sell,
    -- Category info
    pc.category_id,
    pc.category_name,
    -- Brand info
    b.brand_id,
    b.brand_name,
    -- Warehouse info
    w.warehouse_id,
    w.warehouse_name
FROM
    inventory i
    JOIN products p            ON i.product_id = p.product_id
    JOIN product_categories pc ON p.category_id = pc.category_id
    JOIN brands b              ON p.brand_id = b.brand_id
    JOIN warehouses w          ON i.warehouse_id = w.warehouse_id;


-- ── 3. vw_supplier_performance ────────────────────────────
-- Aggregates purchase orders to measure supplier reliability, fulfillment rates, and delivery speeds.
-- Primary use: Supplier auditing, lead time optimization.
DROP VIEW IF EXISTS vw_supplier_performance;
CREATE VIEW vw_supplier_performance AS
SELECT
    s.supplier_id,
    s.supplier_name,
    s.supplier_type,
    s.city AS supplier_city,
    s.payment_terms,
    -- Aggregated order metrics
    COUNT(DISTINCT po.purchase_id) AS total_procurement_events,
    COUNT(po.po_id) AS total_line_items_ordered,
    SUM(po.quantity_ordered) AS total_units_ordered,
    SUM(po.quantity_received) AS total_units_received,
    -- Fulfillment rate (units received / units ordered)
    ROUND(SUM(po.quantity_received) * 100.0 / SUM(po.quantity_ordered), 2) AS fulfillment_rate_pct,
    -- Delivery timelines (excluding items not yet delivered / pending)
    SUM(CASE WHEN po.actual_delivery_date IS NOT NULL THEN 1 ELSE 0 END) AS delivered_line_items,
    SUM(CASE WHEN po.actual_delivery_date IS NOT NULL AND po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) AS on_time_deliveries,
    -- On-time delivery rate (on-time / total delivered)
    ROUND(
        SUM(CASE WHEN po.actual_delivery_date IS NOT NULL AND po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN po.actual_delivery_date IS NOT NULL THEN 1 ELSE 0 END), 0), 
        2
    ) AS on_time_delivery_rate_pct,
    -- Average delay in days
    ROUND(
        AVG(CASE WHEN po.actual_delivery_date IS NOT NULL THEN DATEDIFF(po.actual_delivery_date, po.expected_delivery_date) ELSE NULL END),
        1
    ) AS avg_delivery_delay_days
FROM
    suppliers s
    LEFT JOIN purchases pu      ON s.supplier_id = pu.supplier_id
    LEFT JOIN purchase_orders po ON pu.purchase_id = po.purchase_id
GROUP BY
    s.supplier_id, s.supplier_name, s.supplier_type, s.city, s.payment_terms;


-- ── 4. vw_erickshaw_analytics ──────────────────────────────
-- Consolidates e-rickshaw purchase lifecycles including enquiry, booking, and delivery.
-- Primary use: E-rickshaw conversion funnel, model sales trends, festive lift.
DROP VIEW IF EXISTS vw_erickshaw_analytics;
CREATE VIEW vw_erickshaw_analytics AS
SELECT
    er.er_sale_id,
    er.enquiry_date,
    er.booking_date,
    er.delivery_date,
    er.amount AS selling_price,
    er.cost_price,
    er.amount - er.cost_price AS profit_amount,
    ROUND((er.amount - er.cost_price) * 100.0 / er.amount, 2) AS margin_pct,
    er.payment_method,
    er.payment_status,
    er.er_model,
    er.festive_occasion,
    -- Funnel conversions
    DATEDIFF(er.booking_date, er.enquiry_date) AS days_to_convert,
    DATEDIFF(er.delivery_date, er.booking_date) AS days_to_deliver,
    -- Customer info
    c.customer_id,
    c.name AS customer_name,
    c.phone AS customer_phone,
    c.area AS customer_area,
    -- Employee info
    e.employee_id,
    e.name AS employee_name
FROM
    erickshaw_sales er
    JOIN customers c ON er.customer_id = c.customer_id
    JOIN employees e ON er.employee_id = e.employee_id;


-- ── 5. vw_monthly_financials ──────────────────────────────
-- Rolls up monthly sales revenue/profit and operational expenses.
-- Primary use: High-level financial reporting, profit margin trends, operating cost ratios.
-- Written using LEFT JOINs to guarantee MySQL 8.x compatibility without FULL OUTER JOIN support.
DROP VIEW IF EXISTS vw_monthly_financials;
CREATE VIEW vw_monthly_financials AS
WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(sale_date, '%Y-%m') AS `year_month`,
        YEAR(sale_date) AS fiscal_year,
        MONTH(sale_date) AS fiscal_month,
        COUNT(DISTINCT sale_id) AS total_sales_transactions,
        SUM(net_revenue) AS total_sales_revenue,
        SUM(profit_amount) AS total_sales_profit
    FROM (
        SELECT 
            s.sale_id, 
            s.sale_date, 
            ROUND(si.quantity * si.unit_price * (1 - si.discount_pct / 100.0), 2) AS net_revenue,
            si.profit_amount
        FROM sales s
        JOIN sales_items si ON s.sale_id = si.sale_id
    ) sales_sub
    GROUP BY DATE_FORMAT(sale_date, '%Y-%m'), YEAR(sale_date), MONTH(sale_date)
),
monthly_erickshaw_sales AS (
    SELECT
        DATE_FORMAT(booking_date, '%Y-%m') AS `year_month`,
        COUNT(er_sale_id) AS total_erickshaw_transactions,
        SUM(amount) AS total_erickshaw_revenue,
        SUM(amount - cost_price) AS total_erickshaw_profit
    FROM erickshaw_sales
    GROUP BY DATE_FORMAT(booking_date, '%Y-%m')
),
monthly_expenses AS (
    SELECT
        DATE_FORMAT(expense_date, '%Y-%m') AS `year_month`,
        COUNT(expense_id) AS total_expense_entries,
        SUM(amount) AS total_operating_expenses
    FROM expenses
    GROUP BY DATE_FORMAT(expense_date, '%Y-%m')
),
all_months AS (
    SELECT `year_month` FROM monthly_sales
    UNION
    SELECT `year_month` FROM monthly_erickshaw_sales
    UNION
    SELECT `year_month` FROM monthly_expenses
)
SELECT
    am.`year_month`,
    YEAR(STR_TO_DATE(CONCAT(am.`year_month`, '-01'), '%Y-%m-%d')) AS fiscal_year,
    MONTH(STR_TO_DATE(CONCAT(am.`year_month`, '-01'), '%Y-%m-%d')) AS fiscal_month,
    -- Revenue sources
    COALESCE(ms.total_sales_revenue, 0.00) AS retail_sales_revenue,
    COALESCE(mer.total_erickshaw_revenue, 0.00) AS erickshaw_sales_revenue,
    (COALESCE(ms.total_sales_revenue, 0.00) + COALESCE(mer.total_erickshaw_revenue, 0.00)) AS total_gross_revenue,
    -- Profit sources
    COALESCE(ms.total_sales_profit, 0.00) AS retail_sales_profit,
    COALESCE(mer.total_erickshaw_profit, 0.00) AS erickshaw_sales_profit,
    (COALESCE(ms.total_sales_profit, 0.00) + COALESCE(mer.total_erickshaw_profit, 0.00)) AS total_gross_profit,
    -- Profit Margin %
    ROUND(
        (COALESCE(ms.total_sales_profit, 0.00) + COALESCE(mer.total_erickshaw_profit, 0.00)) * 100.0 / 
        NULLIF((COALESCE(ms.total_sales_revenue, 0.00) + COALESCE(mer.total_erickshaw_revenue, 0.00)), 0),
        2
    ) AS gross_profit_margin_pct,
    -- Operating expenses
    COALESCE(me.total_operating_expenses, 0.00) AS operating_expenses,
    -- Net Profit
    (COALESCE(ms.total_sales_profit, 0.00) + COALESCE(mer.total_erickshaw_profit, 0.00) - COALESCE(me.total_operating_expenses, 0.00)) AS net_profit
FROM
    all_months am
    LEFT JOIN monthly_sales ms ON am.`year_month` = ms.`year_month`
    LEFT JOIN monthly_erickshaw_sales mer ON am.`year_month` = mer.`year_month`
    LEFT JOIN monthly_expenses me ON am.`year_month` = me.`year_month`
ORDER BY
    am.`year_month`;
