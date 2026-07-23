-- ============================================================
-- Swastik Traders — Stored Procedures
-- Phase 2: Database Design
-- Version: 1.0  |  Date: July 2026
-- ============================================================

USE swastik_traders_clean;

-- ── 1. sp_monthly_kpi ──────────────────────────────────────
-- Returns monthly financial performance indicators (revenue, COGS, gross/net profit)
-- for a specific month and year.
-- Primary use: Interactive reports and period checks.
DROP PROCEDURE IF EXISTS sp_monthly_kpi;

DELIMITER $$

CREATE PROCEDURE sp_monthly_kpi(
    IN in_month INT,
    IN in_year INT
)
BEGIN
    SELECT 
        `year_month`,
        retail_sales_revenue,
        erickshaw_sales_revenue,
        total_gross_revenue,
        retail_sales_profit,
        erickshaw_sales_profit,
        total_gross_profit,
        gross_profit_margin_pct,
        operating_expenses,
        net_profit
    FROM 
        vw_monthly_financials
    WHERE 
        fiscal_month = in_month 
        AND fiscal_year = in_year;
END$$

DELIMITER ;


-- ── 2. sp_supplier_performance ────────────────────────────
-- Returns performance metrics for a specific supplier by ID.
-- Primary use: Detailed supplier analysis and performance auditing.
DROP PROCEDURE IF EXISTS sp_supplier_performance;

DELIMITER $$

CREATE PROCEDURE sp_supplier_performance(
    IN in_supplier_id INT
)
BEGIN
    SELECT 
        supplier_id,
        supplier_name,
        supplier_type,
        supplier_city,
        payment_terms,
        total_procurement_events,
        total_line_items_ordered,
        total_units_ordered,
        total_units_received,
        fulfillment_rate_pct,
        on_time_delivery_rate_pct,
        avg_delivery_delay_days
    FROM 
        vw_supplier_performance
    WHERE 
        supplier_id = in_supplier_id;
END$$

DELIMITER ;
