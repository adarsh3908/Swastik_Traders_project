-- ============================================================
-- Swastik Traders — Database Events
-- Phase 2: Database Design
-- Version: 1.0  |  Date: July 2026
-- ============================================================

USE swastik_traders;

-- ── 1. evt_daily_dead_stock_refresh ──────────────────────
-- Runs daily to identify products that have not had any sales in the last 90 days.
-- These are flagged as dead stock in the inventory table.
-- It also flags static slow-moving products (e.g. specific slow colors, grits, stirrers).
DROP EVENT IF EXISTS evt_daily_dead_stock_refresh;

DELIMITER $$

CREATE EVENT evt_daily_dead_stock_refresh
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR) -- Starts tomorrow at 2:00 AM
ON COMPLETION PRESERVE
DO
BEGIN
    -- 1. Reset all dead stock flags to 0
    UPDATE inventory 
    SET dead_stock_flag = 0;
    
    -- 2. Set dead_stock_flag = 1 for known slow-moving product profiles
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

    -- 3. Set dead_stock_flag = 1 for items that have had no sales in the last 90 days
    -- We use subqueries to find items with recent sales and flag the remainder.
    -- (Uses the maximum sale date in the database as a reference point to accommodate historical datasets)
    UPDATE inventory i
    SET i.dead_stock_flag = 1
    WHERE (i.product_id, i.warehouse_id) NOT IN (
        SELECT DISTINCT si.product_id, si.warehouse_id
        FROM sales_items si
        JOIN sales s ON si.sale_id = s.sale_id
        WHERE s.sale_date >= DATE_SUB(
            (SELECT COALESCE(MAX(sale_date), CURRENT_DATE) FROM sales), 
            INTERVAL 90 DAY
        )
    );
END$$

DELIMITER ;
