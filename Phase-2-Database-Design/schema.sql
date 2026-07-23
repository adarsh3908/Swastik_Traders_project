-- ============================================================
-- Swastik Traders — MySQL Schema
-- Phase 2: Database Design
-- Version: 1.0  |  Date: July 2026
-- ============================================================
-- HOW TO USE:
--   1. Open MySQL Workbench
--   2. File → Open SQL Script → select this file
--   3. Click ⚡ (Execute All) — top toolbar
--   4. Refresh the Schema panel — "swastik_traders" appears
-- ============================================================

CREATE DATABASE IF NOT EXISTS swastik_traders
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE swastik_traders;

-- Disable FK checks during table creation (re-enabled at end)
SET FOREIGN_KEY_CHECKS = 0;


-- ============================================================
-- DIMENSION TABLES
-- (Created first — no dependencies on other tables)
-- ============================================================

-- ── Table 1: product_categories ───────────────────────────
-- Hierarchy: Paint → Interior/Exterior/Primer/Putty/Enamel
--            Accessories → Brush/Roller/Other
--            E-Rickshaw
DROP TABLE IF EXISTS product_categories;
CREATE TABLE product_categories (
    category_id         INT             NOT NULL AUTO_INCREMENT,
    category_name       VARCHAR(100)    NOT NULL,
    parent_category_id  INT             NULL,           -- Self-reference: NULL = top-level
    description         TEXT            NULL,
    PRIMARY KEY (category_id),
    CONSTRAINT fk_cat_parent
        FOREIGN KEY (parent_category_id)
        REFERENCES product_categories(category_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_cat_parent ON product_categories(parent_category_id);


-- ── Table 2: brands ───────────────────────────────────────
-- Asian Paints, Indigo Paints, JSW Paints, Saarthi, City Life
DROP TABLE IF EXISTS brands;
CREATE TABLE brands (
    brand_id            INT             NOT NULL AUTO_INCREMENT,
    brand_name          VARCHAR(100)    NOT NULL,
    brand_type          VARCHAR(50)     NOT NULL,       -- 'paint' / 'erickshaw'
    country_of_origin   VARCHAR(50)     NULL,
    contact_person      VARCHAR(100)    NULL,
    PRIMARY KEY (brand_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 3: products ─────────────────────────────────────
-- SKU = Brand × Product Name × Color × Pack Size
-- ~202 rows. Putty always White; emulsions come in 3 colors.
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    product_id          INT             NOT NULL AUTO_INCREMENT,
    product_name        VARCHAR(200)    NOT NULL,
    category_id         INT             NOT NULL,
    brand_id            INT             NOT NULL,
    color               VARCHAR(50)     NULL,           -- NULL for accessories/e-rickshaws; 'White'/'Ivory'/'Cream' for paint
    pack_size           VARCHAR(30)     NOT NULL,       -- e.g. '20L', '40kg', '1 piece'
    unit                VARCHAR(20)     NOT NULL,       -- 'litre' / 'kg' / 'piece'
    cost_price          DECIMAL(10,2)   NOT NULL,
    selling_price       DECIMAL(10,2)   NOT NULL,
    margin_pct          DECIMAL(5,2)    NULL,           -- Derived; putty ~7%, accessories ~35%
    min_stock_level     INT             NOT NULL DEFAULT 10,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    PRIMARY KEY (product_id),
    CONSTRAINT fk_prod_category
        FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    CONSTRAINT fk_prod_brand
        FOREIGN KEY (brand_id)    REFERENCES brands(brand_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_prod_category  ON products(category_id);
CREATE INDEX idx_prod_brand     ON products(brand_id);
CREATE INDEX idx_prod_color     ON products(color);
CREATE INDEX idx_prod_active    ON products(is_active);


-- ── Table 4: suppliers ────────────────────────────────────
-- All external parties: brand distributors, accessory wholesalers, e-rickshaw OEMs
DROP TABLE IF EXISTS suppliers;
CREATE TABLE suppliers (
    supplier_id         INT             NOT NULL AUTO_INCREMENT,
    supplier_name       VARCHAR(150)    NOT NULL,
    supplier_type       ENUM(
                            'paint_distributor',
                            'accessory_wholesaler',
                            'erickshaw_oem'
                        )               NOT NULL,
    contact_person      VARCHAR(100)    NULL,
    phone               VARCHAR(15)     NULL,
    city                VARCHAR(100)    NULL,
    payment_terms       ENUM(
                            'immediate',
                            '7_days',
                            '15_days',
                            '30_days'
                        )               NOT NULL DEFAULT 'immediate',
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    PRIMARY KEY (supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 5: warehouses ───────────────────────────────────
-- Godown 1 (active Jul 2022), Godown 2 (fully active Feb 2025)
DROP TABLE IF EXISTS warehouses;
CREATE TABLE warehouses (
    warehouse_id            INT         NOT NULL AUTO_INCREMENT,
    warehouse_name          VARCHAR(100) NOT NULL,
    capacity_sqft           INT         NULL,
    is_active               TINYINT(1)  NOT NULL DEFAULT 1,
    operationalized_date    DATE        NOT NULL,
    PRIMARY KEY (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 6: employees ────────────────────────────────────
-- 7 total: 1 owner, 2 co-founders, 4 labourers
DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
    employee_id         INT             NOT NULL AUTO_INCREMENT,
    name                VARCHAR(150)    NOT NULL,
    role                ENUM(
                            'owner',
                            'co_founder',
                            'labour'
                        )               NOT NULL,
    phone               VARCHAR(15)     NULL,
    monthly_salary      DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    hire_date           DATE            NOT NULL,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    PRIMARY KEY (employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 7: promotions ───────────────────────────────────
-- Festival + seasonal campaigns. NULL category = applies to all.
DROP TABLE IF EXISTS promotions;
CREATE TABLE promotions (
    promotion_id            INT         NOT NULL AUTO_INCREMENT,
    promo_name              VARCHAR(150) NOT NULL,
    promo_type              ENUM(
                                'discount',
                                'bundle',
                                'seasonal',
                                'festival'
                            )           NOT NULL,
    start_date              DATE        NOT NULL,
    end_date                DATE        NOT NULL,
    discount_pct            DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    applicable_category_id  INT         NULL,           -- NULL = all categories
    min_purchase_amount     DECIMAL(10,2) NULL,
    PRIMARY KEY (promotion_id),
    CONSTRAINT fk_promo_category
        FOREIGN KEY (applicable_category_id)
        REFERENCES product_categories(category_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 8: customers ────────────────────────────────────
-- Retail buyers, contractors, painters — all in-store walk-ins
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id         INT             NOT NULL AUTO_INCREMENT,
    name                VARCHAR(150)    NOT NULL,
    phone               VARCHAR(15)     NULL,           -- ~4% malformed (dirty data)
    address             VARCHAR(255)    NULL,           -- ~8% missing (dirty data)
    area                VARCHAR(100)    NULL,           -- Mohalla / locality in Ballia
    customer_type       ENUM(
                            'retail',
                            'contractor',
                            'painter'
                        )               NOT NULL DEFAULT 'retail',
    first_purchase_date DATE            NULL,           -- Filled during Phase 3 ETL
    PRIMARY KEY (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_cust_type  ON customers(customer_type);
CREATE INDEX idx_cust_area  ON customers(area);


-- ============================================================
-- FACT / TRANSACTIONAL TABLES
-- (Created after all dimension tables)
-- ============================================================

-- ── Table 9: inventory ────────────────────────────────────
-- Point-in-time snapshot; product × godown stock levels
DROP TABLE IF EXISTS inventory;
CREATE TABLE inventory (
    inventory_id        INT             NOT NULL AUTO_INCREMENT,
    product_id          INT             NOT NULL,
    warehouse_id        INT             NOT NULL,
    quantity_in_stock   INT             NOT NULL DEFAULT 0,
    last_updated        DATE            NOT NULL,
    reorder_level       INT             NOT NULL DEFAULT 5,
    dead_stock_flag     TINYINT(1)      NOT NULL DEFAULT 0,  -- 1 = no movement 90+ days
    PRIMARY KEY (inventory_id),
    CONSTRAINT fk_inv_product
        FOREIGN KEY (product_id)    REFERENCES products(product_id),
    CONSTRAINT fk_inv_warehouse
        FOREIGN KEY (warehouse_id)  REFERENCES warehouses(warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_inv_product    ON inventory(product_id);
CREATE INDEX idx_inv_warehouse  ON inventory(warehouse_id);
CREATE INDEX idx_inv_deadstock  ON inventory(dead_stock_flag);


-- ── Table 10: purchases ───────────────────────────────────
-- Procurement event header (Swastik buying from supplier)
DROP TABLE IF EXISTS purchases;
CREATE TABLE purchases (
    purchase_id         INT             NOT NULL AUTO_INCREMENT,
    supplier_id         INT             NOT NULL,
    warehouse_id        INT             NOT NULL,       -- Godown receiving the stock
    purchase_date       DATE            NOT NULL,
    total_amount        DECIMAL(12,2)   NOT NULL,
    payment_status      ENUM(
                            'paid',
                            'pending',
                            'partial'
                        )               NOT NULL DEFAULT 'paid',
    invoice_number      VARCHAR(50)     NULL,
    PRIMARY KEY (purchase_id),
    CONSTRAINT fk_purch_supplier
        FOREIGN KEY (supplier_id)   REFERENCES suppliers(supplier_id),
    CONSTRAINT fk_purch_warehouse
        FOREIGN KEY (warehouse_id)  REFERENCES warehouses(warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_purch_date     ON purchases(purchase_date);
CREATE INDEX idx_purch_supplier ON purchases(supplier_id);


-- ── Table 11: purchase_orders ─────────────────────────────
-- Line items for each procurement event
DROP TABLE IF EXISTS purchase_orders;
CREATE TABLE purchase_orders (
    po_id                   INT         NOT NULL AUTO_INCREMENT,
    purchase_id             INT         NOT NULL,
    product_id              INT         NOT NULL,
    quantity_ordered        INT         NOT NULL,
    quantity_received       INT         NOT NULL DEFAULT 0,  -- May be < ordered
    unit_price              DECIMAL(10,2) NOT NULL,
    po_date                 DATE        NOT NULL,
    expected_delivery_date  DATE        NOT NULL,
    actual_delivery_date    DATE        NULL,           -- NULL = not yet delivered / missing (dirty)
    status                  ENUM(
                                'pending',
                                'partial',
                                'complete',
                                'cancelled'
                            )           NOT NULL DEFAULT 'pending',
    PRIMARY KEY (po_id),
    CONSTRAINT fk_po_purchase
        FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
    CONSTRAINT fk_po_product
        FOREIGN KEY (product_id)  REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_po_purchase    ON purchase_orders(purchase_id);
CREATE INDEX idx_po_product     ON purchase_orders(product_id);
CREATE INDEX idx_po_status      ON purchase_orders(status);


-- ── Table 12: sales ───────────────────────────────────────
-- All in-store customer transactions (no online / no B2B selling)
DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
    sale_id             INT             NOT NULL AUTO_INCREMENT,
    customer_id         INT             NOT NULL,
    employee_id         INT             NOT NULL,       -- Owner or co-founder handled billing
    sale_date           DATE            NOT NULL,
    total_amount        DECIMAL(12,2)   NOT NULL,
    payment_method      ENUM(
                            'cash',
                            'upi',
                            'bank_transfer'
                        )               NOT NULL,       -- No cheque, no credit, no card
    payment_status      ENUM(
                            'paid',
                            'pending'
                        )               NOT NULL DEFAULT 'paid',
    promotion_id        INT             NULL,           -- NULL if no active promo
    PRIMARY KEY (sale_id),
    CONSTRAINT fk_sale_customer
        FOREIGN KEY (customer_id)   REFERENCES customers(customer_id),
    CONSTRAINT fk_sale_employee
        FOREIGN KEY (employee_id)   REFERENCES employees(employee_id),
    CONSTRAINT fk_sale_promo
        FOREIGN KEY (promotion_id)  REFERENCES promotions(promotion_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_sale_date      ON sales(sale_date);
CREATE INDEX idx_sale_customer  ON sales(customer_id);
CREATE INDEX idx_sale_employee  ON sales(employee_id);
CREATE INDEX idx_sale_method    ON sales(payment_method);


-- ── Table 13: sales_items ─────────────────────────────────
-- Line-level: one row per product per sale
-- Primary fact table for margin analysis
DROP TABLE IF EXISTS sales_items;
CREATE TABLE sales_items (
    sale_item_id        INT             NOT NULL AUTO_INCREMENT,
    sale_id             INT             NOT NULL,
    product_id          INT             NOT NULL,
    warehouse_id        INT             NOT NULL,       -- Godown stock was drawn from
    quantity            INT             NOT NULL,
    unit_price          DECIMAL(10,2)   NOT NULL,
    cost_price          DECIMAL(10,2)   NOT NULL,
    discount_pct        DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    profit_amount       DECIMAL(10,2)   NOT NULL,       -- (net_price - cost) × qty
    PRIMARY KEY (sale_item_id),
    CONSTRAINT fk_si_sale
        FOREIGN KEY (sale_id)       REFERENCES sales(sale_id),
    CONSTRAINT fk_si_product
        FOREIGN KEY (product_id)    REFERENCES products(product_id),
    CONSTRAINT fk_si_warehouse
        FOREIGN KEY (warehouse_id)  REFERENCES warehouses(warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_si_sale        ON sales_items(sale_id);
CREATE INDEX idx_si_product     ON sales_items(product_id);
CREATE INDEX idx_si_warehouse   ON sales_items(warehouse_id);


-- ── Table 14: sales_returns ───────────────────────────────
-- Very rare (~1.5%). Mostly wrong colour ordered.
-- No e-rickshaw returns.
DROP TABLE IF EXISTS sales_returns;
CREATE TABLE sales_returns (
    return_id           INT             NOT NULL AUTO_INCREMENT,
    sale_id             INT             NOT NULL,
    product_id          INT             NOT NULL,
    return_date         DATE            NOT NULL,
    quantity_returned   INT             NOT NULL,
    reason              VARCHAR(255)    NULL,
    refund_amount       DECIMAL(10,2)   NOT NULL,
    status              ENUM(
                            'processed',
                            'pending'
                        )               NOT NULL DEFAULT 'pending',
    PRIMARY KEY (return_id),
    CONSTRAINT fk_ret_sale
        FOREIGN KEY (sale_id)       REFERENCES sales(sale_id),
    CONSTRAINT fk_ret_product
        FOREIGN KEY (product_id)    REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_ret_sale ON sales_returns(sale_id);


-- ── Table 15: payments ────────────────────────────────────
-- 1-to-1 with sales. Method: cash / UPI / bank_transfer only.
DROP TABLE IF EXISTS payments;
CREATE TABLE payments (
    payment_id          INT             NOT NULL AUTO_INCREMENT,
    sale_id             INT             NOT NULL,
    payment_method      ENUM(
                            'cash',
                            'upi',
                            'bank_transfer'
                        )               NOT NULL,
    payment_date        DATE            NOT NULL,
    amount              DECIMAL(12,2)   NOT NULL,
    payment_status      ENUM(
                            'completed',
                            'pending'
                        )               NOT NULL DEFAULT 'completed',
    transaction_ref     VARCHAR(100)    NULL,           -- UPI txn ID / bank ref; NULL for cash
    PRIMARY KEY (payment_id),
    CONSTRAINT fk_pay_sale
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_pay_sale   ON payments(sale_id);
CREATE INDEX idx_pay_date   ON payments(payment_date);
CREATE INDEX idx_pay_method ON payments(payment_method);


-- ── Table 16: expenses ────────────────────────────────────
-- No rent (property owned). Categories: salary, utilities, maintenance,
-- marketing (organic), one_time_setup (~10L in 2022).
DROP TABLE IF EXISTS expenses;
CREATE TABLE expenses (
    expense_id          INT             NOT NULL AUTO_INCREMENT,
    expense_date        DATE            NOT NULL,
    category            ENUM(
                            'salary',
                            'utilities',
                            'maintenance',
                            'marketing',
                            'one_time_setup'
                        )               NOT NULL,
    amount              DECIMAL(10,2)   NOT NULL,
    approved_by         INT             NULL,           -- FK → employees
    description         TEXT            NULL,
    PRIMARY KEY (expense_id),
    CONSTRAINT fk_exp_employee
        FOREIGN KEY (approved_by) REFERENCES employees(employee_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_exp_date       ON expenses(expense_date);
CREATE INDEX idx_exp_category   ON expenses(category);


-- ── Table 17: erickshaw_sales ─────────────────────────────
-- Low frequency: ~1 per fortnight base rate.
-- Festival spikes: Akshaya Tritiya, Diwali, Navratri → 2–3/week.
-- festive_occasion is NULL on non-festival dates.
DROP TABLE IF EXISTS erickshaw_sales;
CREATE TABLE erickshaw_sales (
    er_sale_id          INT             NOT NULL AUTO_INCREMENT,
    customer_id         INT             NOT NULL,
    employee_id         INT             NOT NULL,
    product_id          INT             NOT NULL,       -- E-Rickshaw model SKU
    enquiry_date        DATE            NULL,
    booking_date        DATE            NOT NULL,
    delivery_date       DATE            NULL,
    amount              DECIMAL(12,2)   NOT NULL,
    cost_price          DECIMAL(12,2)   NOT NULL,
    payment_method      ENUM(
                            'cash',
                            'upi',
                            'bank_transfer'
                        )               NOT NULL,
    payment_status      ENUM(
                            'paid',
                            'pending',
                            'partial'
                        )               NOT NULL DEFAULT 'paid',
    er_model            VARCHAR(100)    NOT NULL,       -- Denormalized for quick querying
    festive_occasion    VARCHAR(100)    NULL,           -- 'Akshaya Tritiya' / 'Diwali' / NULL
    PRIMARY KEY (er_sale_id),
    CONSTRAINT fk_er_customer
        FOREIGN KEY (customer_id)   REFERENCES customers(customer_id),
    CONSTRAINT fk_er_employee
        FOREIGN KEY (employee_id)   REFERENCES employees(employee_id),
    CONSTRAINT fk_er_product
        FOREIGN KEY (product_id)    REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_er_booking     ON erickshaw_sales(booking_date);
CREATE INDEX idx_er_customer    ON erickshaw_sales(customer_id);
CREATE INDEX idx_er_festive     ON erickshaw_sales(festive_occasion);


-- ── Table 18: customer_feedback ───────────────────────────
-- In-store + WhatsApp + Google Maps reviews (merged).
-- sentiment column left NULL here — filled by Phase 6 NLP model.
DROP TABLE IF EXISTS customer_feedback;
CREATE TABLE customer_feedback (
    feedback_id         INT             NOT NULL AUTO_INCREMENT,
    customer_id         INT             NULL,           -- NULL for anonymous
    sale_id             INT             NULL,           -- NULL for general feedback
    feedback_date       DATE            NOT NULL,
    source              ENUM(
                            'in_store',
                            'whatsapp',
                            'google_maps'
                        )               NOT NULL,
    rating              INT             NOT NULL,
    review_text         TEXT            NULL,           -- English/Hinglish mix
    sentiment           ENUM(
                            'positive',
                            'neutral',
                            'negative'
                        )               NULL,           -- Populated in Phase 6
    feedback_category   ENUM(
                            'product_quality',
                            'service',
                            'price',
                            'availability'
                        )               NULL,
    PRIMARY KEY (feedback_id),
    CONSTRAINT fk_fb_customer
        FOREIGN KEY (customer_id)   REFERENCES customers(customer_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_fb_sale
        FOREIGN KEY (sale_id)       REFERENCES sales(sale_id)
        ON DELETE SET NULL,
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_fb_customer    ON customer_feedback(customer_id);
CREATE INDEX idx_fb_date        ON customer_feedback(feedback_date);
CREATE INDEX idx_fb_rating      ON customer_feedback(rating);


-- ============================================================
-- EXTERNAL REFERENCE TABLES
-- (Used to drive generator correlations; not core analytics)
-- ============================================================

-- ── Table 19: weather ─────────────────────────────────────
DROP TABLE IF EXISTS weather;
CREATE TABLE weather (
    weather_id          INT             NOT NULL AUTO_INCREMENT,
    date                DATE            NOT NULL,
    city                VARCHAR(50)     NOT NULL DEFAULT 'Ballia',
    temperature_max     DECIMAL(5,2)    NULL,
    rainfall_mm         DECIMAL(7,2)    NULL,
    season              ENUM(
                            'pre_monsoon',
                            'monsoon',
                            'post_monsoon',
                            'winter',
                            'summer'
                        )               NOT NULL,
    is_extreme          TINYINT(1)      NOT NULL DEFAULT 0,
    PRIMARY KEY (weather_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_weather_date   ON weather(date);
CREATE INDEX idx_weather_season ON weather(season);


-- ── Table 20: fuel_prices ─────────────────────────────────
DROP TABLE IF EXISTS fuel_prices;
CREATE TABLE fuel_prices (
    fuel_price_id       INT             NOT NULL AUTO_INCREMENT,
    date                DATE            NOT NULL,
    petrol_price        DECIMAL(6,2)    NOT NULL,
    diesel_price        DECIMAL(6,2)    NOT NULL,
    PRIMARY KEY (fuel_price_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_fuel_date ON fuel_prices(date);


-- ── Table 21: inflation ───────────────────────────────────
DROP TABLE IF EXISTS inflation;
CREATE TABLE inflation (
    inflation_id        INT             NOT NULL AUTO_INCREMENT,
    month               INT             NOT NULL,
    year                INT             NOT NULL,
    cpi_index           DECIMAL(8,3)    NOT NULL,
    inflation_rate_pct  DECIMAL(5,2)    NOT NULL,
    PRIMARY KEY (inflation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_inflation_ym ON inflation(year, month);


-- ============================================================
-- Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;
-- ============================================================

-- Quick confirmation query — run this after executing:
SELECT
    table_name              AS `Table`,
    table_rows              AS `Approx Rows`,
    ROUND(data_length/1024) AS `Data KB`
FROM
    information_schema.tables
WHERE
    table_schema = 'swastik_traders'
ORDER BY
    table_name;
