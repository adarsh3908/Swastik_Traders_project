-- ============================================================
-- Swastik Traders — Clean & Enriched Schema
-- Phase 3: ETL & Data Cleaning
-- Version: 1.0  |  Date: July 2026
-- ============================================================

CREATE DATABASE IF NOT EXISTS swastik_traders_clean
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE swastik_traders_clean;

-- Disable FK checks during table creation
SET FOREIGN_KEY_CHECKS = 0;


-- ── Table 1: product_categories ───────────────────────────
DROP TABLE IF EXISTS product_categories;
CREATE TABLE product_categories (
    category_id         INT             NOT NULL AUTO_INCREMENT,
    category_name       VARCHAR(100)    NOT NULL,
    parent_category_id  INT             NULL,
    description         TEXT            NULL,
    PRIMARY KEY (category_id),
    CONSTRAINT fk_cat_parent
        FOREIGN KEY (parent_category_id)
        REFERENCES product_categories(category_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_cat_parent ON product_categories(parent_category_id);


-- ── Table 2: brands ───────────────────────────────────────
DROP TABLE IF EXISTS brands;
CREATE TABLE brands (
    brand_id            INT             NOT NULL AUTO_INCREMENT,
    brand_name          VARCHAR(100)    NOT NULL,
    brand_type          VARCHAR(50)     NOT NULL,
    country_of_origin   VARCHAR(50)     NULL,
    contact_person      VARCHAR(100)    NULL,
    PRIMARY KEY (brand_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 3: products (Enriched with Price Bucket & Coverage)
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    product_id          INT             NOT NULL AUTO_INCREMENT,
    product_name        VARCHAR(200)    NOT NULL,
    category_id         INT             NOT NULL,
    brand_id            INT             NOT NULL,
    color               VARCHAR(50)     NULL,
    pack_size           VARCHAR(30)     NOT NULL,
    unit                VARCHAR(20)     NOT NULL,
    cost_price          DECIMAL(10,2)   NOT NULL,
    selling_price       DECIMAL(10,2)   NOT NULL,
    margin_pct          DECIMAL(5,2)    NULL,
    min_stock_level     INT             NOT NULL DEFAULT 10,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    -- Engineered Features
    price_bucket        VARCHAR(20)     NOT NULL DEFAULT 'Medium',
    paint_coverage_sqft_estimate DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (product_id),
    CONSTRAINT fk_prod_category
        FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    CONSTRAINT fk_prod_brand
        FOREIGN KEY (brand_id)    REFERENCES brands(brand_id),
    CONSTRAINT chk_prices
        CHECK (cost_price >= 0.00 AND selling_price >= 0.00),
    CONSTRAINT chk_price_bucket
        CHECK (price_bucket IN ('Low', 'Medium', 'High'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_prod_category  ON products(category_id);
CREATE INDEX idx_prod_brand     ON products(brand_id);
CREATE INDEX idx_prod_active    ON products(is_active);
CREATE INDEX idx_prod_price_bkt ON products(price_bucket);


-- ── Table 4: suppliers ────────────────────────────────────
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
    applicable_category_id  INT         NULL,
    min_purchase_amount     DECIMAL(10,2) NULL,
    PRIMARY KEY (promotion_id),
    CONSTRAINT fk_promo_category
        FOREIGN KEY (applicable_category_id)
        REFERENCES product_categories(category_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 8: customers (Enriched with RFM Segments, CLV, Phone Validity)
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id         INT             NOT NULL AUTO_INCREMENT,
    name                VARCHAR(150)    NOT NULL,
    phone               VARCHAR(15)     NULL,
    address             VARCHAR(255)    NOT NULL DEFAULT 'Not Provided',
    area                VARCHAR(100)    NULL,
    customer_type       ENUM(
                            'retail',
                            'contractor',
                            'painter'
                        )               NOT NULL DEFAULT 'retail',
    -- Engineered Features
    first_purchase_date DATE            NULL,
    clv                 DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    purchase_frequency  INT             NOT NULL DEFAULT 0,
    recency             INT             NOT NULL DEFAULT 9999,
    avg_basket_size     DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    customer_segment    VARCHAR(50)     NOT NULL DEFAULT 'Lost',
    repeat_customer_flag TINYINT(1)     NOT NULL DEFAULT 0,
    is_valid_phone      TINYINT(1)      NOT NULL DEFAULT 0,
    PRIMARY KEY (customer_id),
    CONSTRAINT chk_cust_phone
        CHECK (phone IS NULL OR phone REGEXP '^[0-9]+$'),
    CONSTRAINT chk_cust_segment
        CHECK (customer_segment IN ('Champions', 'Loyal Customers', 'Promising', 'Need Attention', 'Lost')),
    CONSTRAINT chk_repeat_cust
        CHECK (repeat_customer_flag IN (0, 1)),
    CONSTRAINT chk_valid_phone
        CHECK (is_valid_phone IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_cust_type      ON customers(customer_type);
CREATE INDEX idx_cust_segment   ON customers(customer_segment);
CREATE INDEX idx_cust_clv       ON customers(clv);


-- ── Table 9: inventory ────────────────────────────────────
DROP TABLE IF EXISTS inventory;
CREATE TABLE inventory (
    inventory_id        INT             NOT NULL AUTO_INCREMENT,
    product_id          INT             NOT NULL,
    warehouse_id        INT             NOT NULL,
    quantity_in_stock   INT             NOT NULL DEFAULT 0,
    last_updated        DATE            NOT NULL,
    reorder_level       INT             NOT NULL DEFAULT 5,
    dead_stock_flag     TINYINT(1)      NOT NULL DEFAULT 0,
    PRIMARY KEY (inventory_id),
    CONSTRAINT fk_inv_product
        FOREIGN KEY (product_id)    REFERENCES products(product_id),
    CONSTRAINT fk_inv_warehouse
        FOREIGN KEY (warehouse_id)  REFERENCES warehouses(warehouse_id),
    CONSTRAINT chk_inv_dead_flag
        CHECK (dead_stock_flag IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_inv_product    ON inventory(product_id);
CREATE INDEX idx_inv_warehouse  ON inventory(warehouse_id);


-- ── Table 10: purchases ───────────────────────────────────
DROP TABLE IF EXISTS purchases;
CREATE TABLE purchases (
    purchase_id         INT             NOT NULL AUTO_INCREMENT,
    supplier_id         INT             NOT NULL,
    warehouse_id        INT             NOT NULL,
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


-- ── Table 11: purchase_orders (Enriched with Delivery Delay)
DROP TABLE IF EXISTS purchase_orders;
CREATE TABLE purchase_orders (
    po_id                   INT         NOT NULL AUTO_INCREMENT,
    purchase_id             INT         NOT NULL,
    product_id              INT         NOT NULL,
    quantity_ordered        INT         NOT NULL,
    quantity_received       INT         NOT NULL DEFAULT 0,
    unit_price              DECIMAL(10,2) NOT NULL,
    po_date                 DATE        NOT NULL,
    expected_delivery_date  DATE        NOT NULL,
    actual_delivery_date    DATE        NULL,
    status                  ENUM(
                                'pending',
                                'partial',
                                'complete',
                                'cancelled'
                            )           NOT NULL DEFAULT 'pending',
    -- Engineered Features
    delivery_delay_days     INT         NULL,
    PRIMARY KEY (po_id),
    CONSTRAINT fk_po_purchase
        FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
    CONSTRAINT fk_po_product
        FOREIGN KEY (product_id)  REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_po_purchase    ON purchase_orders(purchase_id);
CREATE INDEX idx_po_product     ON purchase_orders(product_id);


-- ── Table 12: sales (Enriched with Seasonality & Expand Context)
DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
    sale_id             INT             NOT NULL AUTO_INCREMENT,
    customer_id         INT             NOT NULL,
    employee_id         INT             NOT NULL,
    sale_date           DATE            NOT NULL,
    total_amount        DECIMAL(12,2)   NOT NULL,
    payment_method      ENUM(
                            'cash',
                            'upi',
                            'bank_transfer'
                        )               NOT NULL,
    payment_status      ENUM(
                            'paid',
                            'pending'
                        )               NOT NULL DEFAULT 'paid',
    promotion_id        INT             NULL,
    -- Engineered Features
    festival_flag       TINYINT(1)      NOT NULL DEFAULT 0,
    holiday_flag        TINYINT(1)      NOT NULL DEFAULT 0,
    season              VARCHAR(20)     NOT NULL DEFAULT 'unknown',
    warehouse_expansion_flag TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (sale_id),
    CONSTRAINT fk_sale_customer
        FOREIGN KEY (customer_id)   REFERENCES customers(customer_id),
    CONSTRAINT fk_sale_employee
        FOREIGN KEY (employee_id)   REFERENCES employees(employee_id),
    CONSTRAINT fk_sale_promo
        FOREIGN KEY (promotion_id)  REFERENCES promotions(promotion_id)
        ON DELETE SET NULL,
    CONSTRAINT chk_sales_fest_flag
        CHECK (festival_flag IN (0, 1)),
    CONSTRAINT chk_sales_hol_flag
        CHECK (holiday_flag IN (0, 1)),
    CONSTRAINT chk_sales_wh_exp_flag
        CHECK (warehouse_expansion_flag IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_sale_date      ON sales(sale_date);
CREATE INDEX idx_sale_customer  ON sales(customer_id);


-- ── Table 13: sales_items ─────────────────────────────────
DROP TABLE IF EXISTS sales_items;
CREATE TABLE sales_items (
    sale_item_id        INT             NOT NULL AUTO_INCREMENT,
    sale_id             INT             NOT NULL,
    product_id          INT             NOT NULL,
    warehouse_id        INT             NOT NULL,
    quantity            INT             NOT NULL,
    unit_price          DECIMAL(10,2)   NOT NULL,
    cost_price          DECIMAL(10,2)   NOT NULL,
    discount_pct        DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    profit_amount       DECIMAL(10,2)   NOT NULL,
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


-- ── Table 14: sales_returns ───────────────────────────────
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


-- ── Table 15: payments ────────────────────────────────────
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
    transaction_ref     VARCHAR(100)    NULL,
    PRIMARY KEY (payment_id),
    CONSTRAINT fk_pay_sale
        FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 16: expenses ────────────────────────────────────
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
    approved_by         INT             NULL,
    description         TEXT            NULL,
    PRIMARY KEY (expense_id),
    CONSTRAINT fk_exp_employee
        FOREIGN KEY (approved_by) REFERENCES employees(employee_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 17: erickshaw_sales ─────────────────────────────
DROP TABLE IF EXISTS erickshaw_sales;
CREATE TABLE erickshaw_sales (
    er_sale_id          INT             NOT NULL AUTO_INCREMENT,
    customer_id         INT             NOT NULL,
    employee_id         INT             NOT NULL,
    product_id          INT             NOT NULL,
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
    er_model            VARCHAR(100)    NOT NULL,
    festive_occasion    VARCHAR(100)    NULL,
    PRIMARY KEY (er_sale_id),
    CONSTRAINT fk_er_customer
        FOREIGN KEY (customer_id)   REFERENCES customers(customer_id),
    CONSTRAINT fk_er_employee
        FOREIGN KEY (employee_id)   REFERENCES employees(employee_id),
    CONSTRAINT fk_er_product
        FOREIGN KEY (product_id)    REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ── Table 18: customer_feedback ───────────────────────────
DROP TABLE IF EXISTS customer_feedback;
CREATE TABLE customer_feedback (
    feedback_id         INT             NOT NULL AUTO_INCREMENT,
    customer_id         INT             NULL,
    sale_id             INT             NULL,
    feedback_date       DATE            NOT NULL,
    source              ENUM(
                            'in_store',
                            'whatsapp',
                            'google_maps'
                        )               NOT NULL,
    rating              INT             NOT NULL,
    review_text         TEXT            NULL,
    sentiment           ENUM(
                            'positive',
                            'neutral',
                            'negative'
                        )               NULL,
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


-- ── Table 20: fuel_prices ─────────────────────────────────
DROP TABLE IF EXISTS fuel_prices;
CREATE TABLE fuel_prices (
    fuel_price_id       INT             NOT NULL AUTO_INCREMENT,
    date                DATE            NOT NULL,
    petrol_price        DECIMAL(6,2)    NOT NULL,
    diesel_price        DECIMAL(6,2)    NOT NULL,
    PRIMARY KEY (fuel_price_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


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


-- Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;
