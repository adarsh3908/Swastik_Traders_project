-- ============================================================
-- Swastik Traders — Database Triggers
-- Phase 2: Database Design
-- Version: 1.0  |  Date: July 2026
-- ============================================================

USE swastik_traders;

-- ── 1. trg_after_sales_item_insert ────────────────────────
-- Automatically deducts stock from the inventory when a sale is completed.
-- Also updates the last_updated date on the inventory record.
DROP TRIGGER IF EXISTS trg_after_sales_item_insert;

DELIMITER $$

CREATE TRIGGER trg_after_sales_item_insert
AFTER INSERT ON sales_items
FOR EACH ROW
BEGIN
    UPDATE inventory
    SET 
        quantity_in_stock = quantity_in_stock - NEW.quantity,
        last_updated = CURRENT_DATE
    WHERE 
        product_id = NEW.product_id
        AND warehouse_id = NEW.warehouse_id;
END$$

DELIMITER ;
