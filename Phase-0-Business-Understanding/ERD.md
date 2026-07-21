# Entity Relationship Diagram (ERD)
## Swastik Traders — Retail Analytics Ecosystem

**Version:** 2.0 (Updated — logistics table removed, schema corrected)
**Date:** July 2026
**Database:** MySQL
**Total Tables:** 21 (18 core + 3 external reference)

> **Change from v1.0:** `logistics` table dropped (not a business concern). `sale_channel` removed from `sales`. Payment methods updated to cash/UPI/bank_transfer only. Employee roles updated. Expense categories updated. `erickshaw_sales` simplified.

---

## ERD — Mermaid Diagram

```mermaid
erDiagram

    %% ─── DIMENSION TABLES ─────────────────────────────────────

    product_categories {
        INT category_id PK
        VARCHAR category_name
        INT parent_category_id FK
        VARCHAR description
    }

    brands {
        INT brand_id PK
        VARCHAR brand_name
        VARCHAR brand_type
        VARCHAR country_of_origin
        VARCHAR contact_person
    }

    products {
        INT product_id PK
        VARCHAR product_name
        INT category_id FK
        INT brand_id FK
        VARCHAR color
        VARCHAR unit
        VARCHAR pack_size
        DECIMAL cost_price
        DECIMAL selling_price
        INT min_stock_level
        BOOLEAN is_active
    }

    customers {
        INT customer_id PK
        VARCHAR name
        VARCHAR phone
        VARCHAR address
        VARCHAR area
        ENUM customer_type
        DATE first_purchase_date
    }

    suppliers {
        INT supplier_id PK
        VARCHAR supplier_name
        ENUM supplier_type
        VARCHAR contact_person
        VARCHAR phone
        VARCHAR city
        ENUM payment_terms
        BOOLEAN is_active
    }

    warehouses {
        INT warehouse_id PK
        VARCHAR warehouse_name
        INT capacity_sqft
        BOOLEAN is_active
        DATE operationalized_date
    }

    employees {
        INT employee_id PK
        VARCHAR name
        ENUM role
        VARCHAR phone
        DECIMAL monthly_salary
        DATE hire_date
        BOOLEAN is_active
    }

    promotions {
        INT promotion_id PK
        VARCHAR promo_name
        ENUM promo_type
        DATE start_date
        DATE end_date
        DECIMAL discount_pct
        INT applicable_category_id FK
        DECIMAL min_purchase_amount
    }

    %% ─── FACT / TRANSACTIONAL TABLES ──────────────────────────

    inventory {
        INT inventory_id PK
        INT product_id FK
        INT warehouse_id FK
        INT quantity_in_stock
        DATETIME last_updated
        INT reorder_level
        BOOLEAN dead_stock_flag
    }

    purchases {
        INT purchase_id PK
        INT supplier_id FK
        INT warehouse_id FK
        DATE purchase_date
        DECIMAL total_amount
        ENUM payment_status
        VARCHAR invoice_number
    }

    purchase_orders {
        INT po_id PK
        INT purchase_id FK
        INT product_id FK
        INT quantity_ordered
        INT quantity_received
        DECIMAL unit_price
        DATE po_date
        DATE expected_delivery_date
        DATE actual_delivery_date
        ENUM status
    }

    sales {
        INT sale_id PK
        INT customer_id FK
        INT employee_id FK
        DATE sale_date
        DECIMAL total_amount
        ENUM payment_method
        ENUM payment_status
        INT promotion_id FK
    }

    sales_items {
        INT sale_item_id PK
        INT sale_id FK
        INT product_id FK
        INT warehouse_id FK
        INT quantity
        DECIMAL unit_price
        DECIMAL cost_price
        DECIMAL discount_pct
        DECIMAL profit_amount
    }

    sales_returns {
        INT return_id PK
        INT sale_id FK
        INT product_id FK
        DATE return_date
        INT quantity_returned
        VARCHAR reason
        DECIMAL refund_amount
        ENUM status
    }

    payments {
        INT payment_id PK
        INT sale_id FK
        ENUM payment_method
        DATE payment_date
        DECIMAL amount
        ENUM payment_status
        VARCHAR transaction_ref
    }

    expenses {
        INT expense_id PK
        DATE expense_date
        ENUM category
        DECIMAL amount
        INT approved_by FK
        TEXT description
    }

    erickshaw_sales {
        INT er_sale_id PK
        INT customer_id FK
        INT employee_id FK
        INT product_id FK
        DATE enquiry_date
        DATE booking_date
        DATE delivery_date
        DECIMAL amount
        DECIMAL cost_price
        ENUM payment_method
        ENUM payment_status
        VARCHAR er_model
        VARCHAR festive_occasion
    }

    customer_feedback {
        INT feedback_id PK
        INT customer_id FK
        INT sale_id FK
        DATE feedback_date
        ENUM source
        INT rating
        TEXT review_text
        ENUM sentiment
        ENUM feedback_category
    }

    %% ─── EXTERNAL REFERENCE TABLES (generator-only) ───────────

    weather {
        INT weather_id PK
        DATE date
        VARCHAR city
        DECIMAL temperature_max
        DECIMAL rainfall_mm
        ENUM season
        BOOLEAN is_extreme
    }

    fuel_prices {
        INT fuel_price_id PK
        DATE date
        DECIMAL petrol_price
        DECIMAL diesel_price
    }

    inflation {
        INT inflation_id PK
        INT month
        INT year
        DECIMAL cpi_index
        DECIMAL inflation_rate_pct
    }

    %% ─── RELATIONSHIPS ─────────────────────────────────────────

    product_categories ||--o{ products : "categorizes"
    product_categories ||--o{ product_categories : "parent of"
    product_categories ||--o{ promotions : "applies to"

    brands ||--o{ products : "manufactures"

    products ||--o{ inventory : "tracked in"
    products ||--o{ purchase_orders : "ordered via"
    products ||--o{ sales_items : "sold as"
    products ||--o{ sales_returns : "returned as"
    products ||--o{ erickshaw_sales : "vehicle model"

    suppliers ||--o{ purchases : "supplies via"

    warehouses ||--o{ inventory : "stores"
    warehouses ||--o{ purchases : "received at"
    warehouses ||--o{ sales_items : "dispatched from"

    customers ||--o{ sales : "places"
    customers ||--o{ erickshaw_sales : "books"
    customers ||--o{ customer_feedback : "provides"

    employees ||--o{ sales : "processes"
    employees ||--o{ erickshaw_sales : "handles"
    employees ||--o{ expenses : "approves"

    promotions ||--o{ sales : "applied in"

    purchases ||--o{ purchase_orders : "contains"

    sales ||--o{ sales_items : "contains"
    sales ||--o{ sales_returns : "returned via"
    sales ||--o{ payments : "paid via"
    sales ||--o{ customer_feedback : "triggers"
```

---

## Table Summary

| # | Table | Type | Est. Rows | Notes |
|---|---|---|---|---|
| 1 | `customers` | Dimension | 500–900 | Local buyers in Ballia area |
| 2 | `products` | Dimension | 80–120 | All brand × product × size SKUs |
| 3 | `product_categories` | Dimension | 8–12 | Interior/Exterior/Putty/Primer/Enamel/Accessory/E-Rickshaw |
| 4 | `brands` | Dimension | 5–6 | Asian Paints, Indigo, JSW, Saarthi, City Life |
| 5 | `suppliers` | Dimension | 15–30 | Brand distributors + accessory wholesalers |
| 6 | `warehouses` | Dimension | 2 | Godown 1 + Godown 2 |
| 7 | `employees` | Dimension | 7 | 1 owner, 2 co-founders, 4 labourers |
| 8 | `promotions` | Dimension | 20–40 | Festival campaigns |
| 9 | `inventory` | Fact (snapshot) | 160–240 | Products × 2 godowns |
| 10 | `purchases` | Fact | 400–700 | Procurement events |
| 11 | `purchase_orders` | Fact | 1,200–2,000 | Line items per procurement |
| 12 | `sales` | Fact | 4,000–7,000 | In-store transactions |
| 13 | `sales_items` | Fact | 10,000–20,000 | Line items per sale |
| 14 | `sales_returns` | Fact | 50–120 | Very rare — paint/e-rickshaw rarely returned |
| 15 | `payments` | Fact | 4,000–7,000 | Cash / UPI / bank transfer |
| 16 | `expenses` | Fact | 400–700 | Monthly salary, utilities, maintenance, marketing |
| 17 | `erickshaw_sales` | Fact | 80–120 | ~1/week or fortnight; festival spikes |
| 18 | `customer_feedback` | Fact | 800–1,500 | In-store + WhatsApp + Google Maps |
| 19 | `weather` | External Ref | ~1,200 | Daily; Ballia, UP |
| 20 | `fuel_prices` | External Ref | ~1,200 | Daily; UP region |
| 21 | `inflation` | External Ref | ~42 | Monthly; general CPI |

**Total estimated rows (core tables):** ~22,000–40,000

---

## Key Design Decisions (v2.0)

1. **`logistics` table dropped:** Delivery is not a tracked business process. Suppliers deliver to godowns directly; customers carry or labourers assist with loading. No dispatch/delivery lifecycle to model.

2. **`sale_channel` removed from `sales`:** All sales are in-store. No field needed.

3. **Payment methods:** `ENUM('cash', 'upi', 'bank_transfer')` only. No cheque, no credit/EMI.

4. **Employee roles:** `ENUM('owner', 'co_founder', 'labour')` — 7 people total. Owner and co-founders handle billing/customer interaction; labourers handle loading, godown management.

5. **Expense categories:** `ENUM('salary', 'utilities', 'maintenance', 'marketing', 'one_time_setup')` — No rent. One-time setup cost (~₹10L) recorded as `one_time_setup` in early 2022 records.

6. **`erickshaw_sales` has `festive_occasion` column:** To capture whether the sale coincided with Akshaya Tritiya, Diwali, Navratri, etc. — enables direct festive correlation analysis without relying solely on date joins.

7. **`sales_returns.quantity` expected to be very low:** Generator should produce returns at ~1–2% of sales volume, primarily for paint (wrong colour ordered) rather than e-rickshaws.

8. **`customers.customer_type`:** `ENUM('retail', 'contractor', 'painter')` — no dealer/B2B selling. All are end-consumers buying for their own use or project.

9. **`products.pack_size`:** Stores the physical size (e.g., "20L", "40kg", "4 inch") as a string alongside the `unit`. This enables SKU-level margin analysis by pack size.

10. **Star schema in Power BI:** `sales_items` acts as the main fact table. `product_categories`, `brands`, `products`, `customers`, and a Date dimension form the star schema. `erickshaw_sales` is a secondary fact table with its own dimension joins.
