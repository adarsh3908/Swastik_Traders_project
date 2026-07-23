-- ============================================================
-- Swastik Traders — Database Verification Queries
-- Phase 2: Post-Load Checks
-- Run in MySQL Workbench AFTER load_data.py completes
-- ============================================================

USE swastik_traders;

-- ── CHECK 1: Row counts for all 21 tables ─────────────────
SELECT 'product_categories' AS `Table`, COUNT(*) AS `Rows` FROM product_categories UNION ALL
SELECT 'brands',            COUNT(*) FROM brands            UNION ALL
SELECT 'products',          COUNT(*) FROM products          UNION ALL
SELECT 'suppliers',         COUNT(*) FROM suppliers         UNION ALL
SELECT 'warehouses',        COUNT(*) FROM warehouses        UNION ALL
SELECT 'employees',         COUNT(*) FROM employees         UNION ALL
SELECT 'promotions',        COUNT(*) FROM promotions        UNION ALL
SELECT 'customers',         COUNT(*) FROM customers         UNION ALL
SELECT 'inventory',         COUNT(*) FROM inventory         UNION ALL
SELECT 'purchases',         COUNT(*) FROM purchases         UNION ALL
SELECT 'purchase_orders',   COUNT(*) FROM purchase_orders   UNION ALL
SELECT 'sales',             COUNT(*) FROM sales             UNION ALL
SELECT 'sales_items',       COUNT(*) FROM sales_items       UNION ALL
SELECT 'payments',          COUNT(*) FROM payments          UNION ALL
SELECT 'sales_returns',     COUNT(*) FROM sales_returns     UNION ALL
SELECT 'erickshaw_sales',   COUNT(*) FROM erickshaw_sales   UNION ALL
SELECT 'expenses',          COUNT(*) FROM expenses          UNION ALL
SELECT 'customer_feedback', COUNT(*) FROM customer_feedback UNION ALL
SELECT 'weather',           COUNT(*) FROM weather           UNION ALL
SELECT 'fuel_prices',       COUNT(*) FROM fuel_prices       UNION ALL
SELECT 'inflation',         COUNT(*) FROM inflation;


-- ── CHECK 2: Putty volume vs margin (key business rule) ───
-- Expected: Putty = highest volume, lowest margin %
SELECT
    pc.category_name                                    AS Category,
    SUM(si.quantity)                                    AS Total_Units_Sold,
    ROUND(AVG((si.unit_price - si.cost_price)
              / si.unit_price * 100), 1)                AS Avg_Margin_Pct,
    ROUND(SUM(si.profit_amount), 0)                     AS Total_Profit_INR
FROM
    sales_items si
    JOIN products p    ON si.product_id  = p.product_id
    JOIN product_categories pc ON p.category_id = pc.category_id
WHERE
    pc.category_id NOT IN (1, 7, 11)  -- exclude parent categories & e-rickshaw
GROUP BY
    pc.category_name
ORDER BY
    Total_Units_Sold DESC;


-- ── CHECK 3: E-rickshaw sales by festival ─────────────────
-- Expected: Akshaya Tritiya and Diwali/Navratri = highest counts
SELECT
    COALESCE(festive_occasion, 'Non-Festival')  AS Occasion,
    COUNT(*)                                     AS Sales_Count,
    ROUND(SUM(amount - cost_price), 0)           AS Total_Margin_INR
FROM
    erickshaw_sales
GROUP BY
    festive_occasion
ORDER BY
    Sales_Count DESC;


-- ── CHECK 4: Monthly revenue trend ────────────────────────
SELECT
    DATE_FORMAT(sale_date, '%Y-%m')             AS Month,
    COUNT(*)                                     AS Transactions,
    ROUND(SUM(total_amount), 0)                  AS Revenue_INR,
    ROUND(AVG(total_amount), 0)                  AS Avg_Basket_INR
FROM
    sales
GROUP BY
    DATE_FORMAT(sale_date, '%Y-%m')
ORDER BY
    Month;


-- ── CHECK 5: Payment method breakdown ─────────────────────
-- Expected: cash dominant for small sales, bank_transfer for large
SELECT
    payment_method,
    COUNT(*)                                    AS Transactions,
    ROUND(SUM(total_amount), 0)                 AS Total_Revenue_INR,
    ROUND(AVG(total_amount), 0)                 AS Avg_Amount_INR
FROM
    sales
GROUP BY
    payment_method
ORDER BY
    Transactions DESC;


-- ── CHECK 6: Customer type distribution ───────────────────
SELECT
    customer_type,
    COUNT(*)                                    AS Customer_Count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS Pct
FROM
    customers
GROUP BY
    customer_type;


-- ── CHECK 7: Dirty data — malformed phones ────────────────
-- Expected: ~4% with phone length < 10
SELECT
    CASE
        WHEN LENGTH(phone) = 10 THEN 'Valid (10 digits)'
        WHEN phone IS NULL       THEN 'NULL'
        ELSE CONCAT('Malformed (', LENGTH(phone), ' digits)')
    END                                         AS Phone_Status,
    COUNT(*)                                    AS Customer_Count
FROM
    customers
GROUP BY
    Phone_Status
ORDER BY
    Customer_Count DESC;


-- ── CHECK 8: Expense breakdown by category ────────────────
-- Expected: salary = largest recurring; one_time_setup = largest single amount
SELECT
    category,
    COUNT(*)                                    AS Entries,
    ROUND(SUM(amount), 0)                       AS Total_INR,
    ROUND(AVG(amount), 0)                       AS Avg_INR
FROM
    expenses
GROUP BY
    category
ORDER BY
    Total_INR DESC;


-- ── CHECK 9: Inventory — dead stock candidates ────────────
-- Products with stock but flag = 1 (no movement in 90+ days)
SELECT
    p.product_name,
    pc.category_name,
    p.color,
    w.warehouse_name,
    i.quantity_in_stock,
    ROUND(i.quantity_in_stock * p.cost_price, 0) AS Locked_Value_INR
FROM
    inventory i
    JOIN products p         ON i.product_id   = p.product_id
    JOIN product_categories pc ON p.category_id = pc.category_id
    JOIN warehouses w        ON i.warehouse_id  = w.warehouse_id
WHERE
    i.dead_stock_flag = 1
ORDER BY
    Locked_Value_INR DESC
LIMIT 20;


-- ── CHECK 10: Supplier on-time delivery rate ───────────────
SELECT
    s.supplier_name,
    s.supplier_type,
    COUNT(po.po_id)                                             AS Total_Orders,
    SUM(CASE WHEN po.actual_delivery_date IS NULL THEN 1 ELSE 0 END) AS Missing_Delivery_Date,
    SUM(CASE
            WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1
            ELSE 0
        END)                                                    AS On_Time,
    ROUND(
        SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(po.po_id), 0), 1
    )                                                           AS On_Time_Pct
FROM
    purchase_orders po
    JOIN purchases pu   ON po.purchase_id  = pu.purchase_id
    JOIN suppliers s    ON pu.supplier_id  = s.supplier_id
WHERE
    po.actual_delivery_date IS NOT NULL
GROUP BY
    s.supplier_id, s.supplier_name, s.supplier_type
ORDER BY
    On_Time_Pct DESC;
    
    
  USE swastik_traders;
SET SQL_SAFE_UPDATES = 0;

-- Flag known slow-moving SKUs as dead stock
UPDATE inventory i
JOIN products p ON i.product_id = p.product_id
SET i.dead_stock_flag = 1
WHERE
    p.color = 'Light Yellow'                           -- slowest colour variant
    OR p.product_name LIKE '%Sandpaper 180 grit%'     -- rarely purchased
    OR p.product_name LIKE '%Sandpaper 60 grit%'
    OR p.product_name LIKE '%Paint Stirrer%'
    OR (p.product_name LIKE '%Cement Putty%' AND i.warehouse_id = 2)  -- Godown 2 opened late
    OR (p.product_name LIKE '%Joie Primer%' AND p.pack_size = '4L');  -- slow JSW primer

SET SQL_SAFE_UPDATES = 1;

-- Check 9 — should now return rows
SELECT
    p.product_name,
    pc.category_name,
    p.color,
    w.warehouse_name,
    i.quantity_in_stock,
    ROUND(i.quantity_in_stock * p.cost_price, 0) AS Locked_Value_INR
FROM inventory i
JOIN products p         ON i.product_id   = p.product_id
JOIN product_categories pc ON p.category_id = pc.category_id
JOIN warehouses w       ON i.warehouse_id  = w.warehouse_id
WHERE i.dead_stock_flag = 1
ORDER BY Locked_Value_INR DESC
LIMIT 20;
