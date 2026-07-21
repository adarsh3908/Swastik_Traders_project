# Data Dictionary
## Swastik Traders — Retail Analytics Ecosystem

**Version:** 2.0 (Updated — logistics dropped, columns corrected)
**Living Document:** Updated at end of each phase
**Date:** July 2026

> **Legend for Signal Type:**
> - **IS** = Generator-Intentional Signal (pattern deliberately encoded)
> - **N** = Noise (random, no intended pattern)
> - **D** = Derived (computed from other columns)
> - **E** = Engineered Feature (added in Phase 3, not generated directly)
> - **REF** = External Reference (generator use only, not in core analytics)

---

## Table 1: `customers`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| customer_id | INT | NO | Primary key, auto-increment | N |
| name | VARCHAR(150) | NO | Customer full name | N |
| phone | VARCHAR(15) | YES | 10-digit mobile number | N (~5% malformed for cleaning exercise) |
| address | VARCHAR(255) | YES | Street/locality address | N |
| area | VARCHAR(100) | YES | Area/mohalla within Ballia | N |
| customer_type | ENUM | NO | `retail` / `contractor` / `painter` — all are end-consumers | IS (contractors buy more putty/primer; painters buy bulk emulsion) |
| first_purchase_date | DATE | YES | Date of first recorded purchase | D (derived during ETL from sales) |

**Notes:**
- No GST field — Swastik does not run formal B2B selling. No GST invoices issued to customers.
- City is always Ballia or nearby UP towns — no city column needed.
- ~800 unique customers expected over 39 months.

---

## Table 2: `products`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| product_id | INT | NO | Primary key | N |
| product_name | VARCHAR(200) | NO | Full product name (e.g., "Asian Paints Tractor Emulsion") | N (~5% naming inconsistencies for cleaning) |
| color | VARCHAR(50) | NO | Color variant: `White` / `Ivory` / `Cream` / `Light Yellow` — `White` for primers and putty (no tinting) | IS (dead stock more likely for slow-moving colors like Light Yellow) |
| category_id | INT | NO | FK → product_categories | N |
| brand_id | INT | NO | FK → brands | N |
| pack_size | VARCHAR(30) | NO | Physical size/quantity (e.g., "20L", "40kg", "4 inch") | N |
| unit | VARCHAR(20) | NO | Measurement unit: `litre` / `kg` / `piece` | N |
| cost_price | DECIMAL(10,2) | NO | Procurement cost per pack | IS (tracks mild inflation over time) |
| selling_price | DECIMAL(10,2) | NO | Standard retail price per pack | IS |
| margin_pct | DECIMAL(5,2) | YES | (selling_price - cost_price) / selling_price × 100 | D |
| min_stock_level | INT | NO | Reorder threshold (units) | N |
| is_active | BOOLEAN | NO | Whether still sold | IS |

**Expected SKU count:** ~80–120 (3 brands × ~8–10 products × 3–4 sizes + accessories + 3 e-rickshaw models)

**Key margin insight baked into generation:**
- Putty: `margin_pct` ≈ 4–8% (lowest)
- Primer: `margin_pct` ≈ 10–15%
- Interior Emulsion: `margin_pct` ≈ 12–20%
- Exterior Emulsion: `margin_pct` ≈ 15–22%
- Accessories (brushes, rollers): `margin_pct` ≈ 25–40% (highest)
- E-Rickshaw: `margin_pct` ≈ 8–15% per unit (high absolute ₹ value)

---

## Table 3: `product_categories`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| category_id | INT | NO | Primary key | N |
| category_name | VARCHAR(100) | NO | Category name | N |
| parent_category_id | INT | YES | Self-ref FK for hierarchy (e.g., Interior Paint under Paint) | N |
| description | TEXT | YES | Category description | N |

**Expected categories:**
- Paint (parent)
  - Interior Paint
  - Exterior Paint
  - Primer
  - Putty
  - Enamel / Distemper
- Accessories (parent)
  - Brush
  - Roller
  - Other Accessory
- E-Rickshaw

---

## Table 4: `brands`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| brand_id | INT | NO | Primary key | N |
| brand_name | VARCHAR(100) | NO | Brand name | N |
| brand_type | VARCHAR(50) | NO | `paint` / `erickshaw` | N |
| country_of_origin | VARCHAR(50) | YES | Country of origin | N |
| contact_person | VARCHAR(100) | YES | Brand rep / distributor contact | N |

**Expected brands:** Asian Paints, Indigo Paints, JSW Paints, Saarthi, City Life

---

## Table 5: `suppliers`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| supplier_id | INT | NO | Primary key | N |
| supplier_name | VARCHAR(150) | NO | Supplier company/distributor name | N |
| supplier_type | ENUM | NO | `paint_distributor` / `accessory_wholesaler` / `erickshaw_oem` | N |
| contact_person | VARCHAR(100) | YES | Point of contact | N |
| phone | VARCHAR(15) | YES | Contact number | N |
| city | VARCHAR(100) | YES | Supplier city (Varanasi / Gorakhpur / Patna area distributors) | N |
| payment_terms | ENUM | NO | `immediate` / `7_days` / `15_days` / `30_days` | IS |
| is_active | BOOLEAN | NO | Whether still in use | IS |

**Note:** Suppliers deliver directly to Godown 1 or Godown 2. ~15–30 suppliers expected.

---

## Table 6: `warehouses`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| warehouse_id | INT | NO | Primary key | N |
| warehouse_name | VARCHAR(100) | NO | `Godown 1` / `Godown 2` | N |
| capacity_sqft | INT | YES | Storage area in sq. ft. | IS (Godown 2 fully operationalized 2025) |
| is_active | BOOLEAN | NO | Operational | N |
| operationalized_date | DATE | NO | When godown became active | IS (Godown 1: mid-2022, Godown 2: 2025) |

**Notes:**
- Both godowns are physically attached to the main shop.
- Warehouse utilization is NOT a KPI — the godowns are small, used for whatever inventory arrives.
- Tracking godowns separately is useful only for inventory allocation queries, not utilization dashboards.

---

## Table 7: `employees`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| employee_id | INT | NO | Primary key | N |
| name | VARCHAR(150) | NO | Employee name | N |
| role | ENUM | NO | `owner` / `co_founder` / `labour` | N |
| phone | VARCHAR(15) | YES | Phone number | N |
| monthly_salary | DECIMAL(10,2) | NO | Monthly salary (₹) | IS (labourers at lower rate; owner/co-founders draw profit, not salary in strict sense) |
| hire_date | DATE | NO | Date of joining | IS |
| is_active | BOOLEAN | NO | Currently employed | IS |

**Breakdown:** 1 owner + 2 co-founders + 4 labourers = 7 employees
**Roles:** Owner and co-founders handle billing, customer interaction, supplier calls. Labourers handle loading, unloading, godown organization.

---

## Table 8: `promotions`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| promotion_id | INT | NO | Primary key | N |
| promo_name | VARCHAR(150) | NO | E.g., `Diwali Paint Offer 2023`, `Akshaya Tritiya E-Rickshaw Deal 2024` | N |
| promo_type | ENUM | NO | `discount` / `bundle` / `seasonal` | N |
| start_date | DATE | NO | Start date | IS (aligned with festival calendar) |
| end_date | DATE | NO | End date | IS |
| discount_pct | DECIMAL(5,2) | NO | Discount percentage | N |
| applicable_category_id | INT | YES | FK → product_categories (NULL = all products) | N |
| min_purchase_amount | DECIMAL(10,2) | YES | Minimum order to qualify | N |

---

## Table 9: `inventory`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| inventory_id | INT | NO | Primary key | N |
| product_id | INT | NO | FK → products | N |
| warehouse_id | INT | NO | FK → warehouses | N |
| quantity_in_stock | INT | NO | Current stock (in pack units) | IS (reflects purchase + sales patterns) |
| last_updated | DATETIME | NO | Last stock movement timestamp | N |
| reorder_level | INT | NO | Alert threshold | N |
| dead_stock_flag | BOOLEAN | NO | No movement in 90+ days → TRUE | D |

---

## Table 10: `purchases`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| purchase_id | INT | NO | Primary key | N |
| supplier_id | INT | NO | FK → suppliers | N |
| warehouse_id | INT | NO | FK → warehouses (Godown 1 or 2) | N |
| purchase_date | DATE | NO | Date of procurement | IS (seasonal restock — pre-monsoon, pre-Diwali) |
| total_amount | DECIMAL(12,2) | NO | Total invoice value | IS |
| payment_status | ENUM | NO | `paid` / `pending` / `partial` | IS |
| invoice_number | VARCHAR(50) | YES | Supplier invoice reference | N |

---

## Table 11: `purchase_orders`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| po_id | INT | NO | Primary key | N |
| purchase_id | INT | NO | FK → purchases | N |
| product_id | INT | NO | FK → products | N |
| quantity_ordered | INT | NO | Units ordered | IS |
| quantity_received | INT | NO | Actual units received | IS (~8% with shortfall) |
| unit_price | DECIMAL(10,2) | NO | Cost per unit at order time | IS |
| po_date | DATE | NO | PO raised date | N |
| expected_delivery_date | DATE | NO | Supplier committed date | N |
| actual_delivery_date | DATE | YES | Actual delivery | IS (some distributors have delay patterns) |
| status | ENUM | NO | `pending` / `partial` / `complete` / `cancelled` | IS |

---

## Table 12: `sales`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| sale_id | INT | NO | Primary key | N |
| customer_id | INT | NO | FK → customers | N |
| employee_id | INT | NO | FK → employees (who billed) | N |
| sale_date | DATE | NO | Transaction date | IS (festival spikes, pre-monsoon paint surge) |
| total_amount | DECIMAL(12,2) | NO | Total sale value | IS |
| payment_method | ENUM | NO | `cash` / `upi` / `bank_transfer` | IS (cash dominant for small purchases, bank transfer for large) |
| payment_status | ENUM | NO | `paid` / `pending` | IS (mostly paid; some pending for known contractor regulars) |
| promotion_id | INT | YES | FK → promotions (NULL if no active promo) | IS |

**Removed column from v1.0:** `sale_channel` — all sales are in-store only.

---

## Table 13: `sales_items`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| sale_item_id | INT | NO | Primary key | N |
| sale_id | INT | NO | FK → sales | N |
| product_id | INT | NO | FK → products | N |
| warehouse_id | INT | NO | FK → warehouses (godown stock drawn from) | N |
| quantity | INT | NO | Units sold (pack units) | IS |
| unit_price | DECIMAL(10,2) | NO | Selling price per pack | IS |
| cost_price | DECIMAL(10,2) | NO | Cost price per pack at sale time | IS |
| discount_pct | DECIMAL(5,2) | NO | Discount applied (0.00 if none) | IS |
| profit_amount | DECIMAL(10,2) | NO | (unit_price × (1-discount) − cost_price) × qty | D |

**Key pattern:** Putty items will appear very frequently in `sales_items` with low `profit_amount`. Accessories will appear less frequently but with high `profit_amount` per unit.

---

## Table 14: `sales_returns`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| return_id | INT | NO | Primary key | N |
| sale_id | INT | NO | FK → sales | N |
| product_id | INT | NO | FK → products | N |
| return_date | DATE | NO | Date of return | N |
| quantity_returned | INT | NO | Units returned | N |
| reason | VARCHAR(255) | YES | Return reason (e.g., "wrong colour ordered") | N |
| refund_amount | DECIMAL(10,2) | NO | Refund value | D |
| status | ENUM | NO | `processed` / `pending` | N |

**Generator note:** Returns should be ~1–2% of sales volume. Paint returns (wrong shade) are slightly more likely than hardware. E-rickshaw returns = 0 in generator.

---

## Table 15: `payments`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| payment_id | INT | NO | Primary key | N |
| sale_id | INT | NO | FK → sales | N |
| payment_method | ENUM | NO | `cash` / `upi` / `bank_transfer` | IS |
| payment_date | DATE | NO | Date payment received | IS (some contractor regulars pay after 1–2 days) |
| amount | DECIMAL(12,2) | NO | Amount paid | N |
| payment_status | ENUM | NO | `completed` / `pending` | IS |
| transaction_ref | VARCHAR(100) | YES | UPI transaction ID or bank transfer ref (NULL for cash) | N |

**Note:** No cheque, no credit/EMI, no card payments.

---

## Table 16: `expenses`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| expense_id | INT | NO | Primary key | N |
| expense_date | DATE | NO | Date of expense | N |
| category | ENUM | NO | `salary` / `utilities` / `maintenance` / `marketing` / `one_time_setup` | N |
| amount | DECIMAL(10,2) | NO | Expense amount | IS |
| approved_by | INT | YES | FK → employees (owner/co-founder) | N |
| description | TEXT | YES | Brief note | N |

**Notes:**
- **No rent** — property is owned.
- `one_time_setup`: ~₹10L recorded as single entry in mid-2022 (shop fit-out, godown setup, initial inventory racks, signage).
- `salary`: Recurring monthly for all 7 employees.
- `utilities`: Electricity, water — recurring monthly.
- `maintenance`: Godown repairs, equipment upkeep — occasional.
- `marketing`: Mostly organic; occasional WhatsApp broadcast, local newspaper ad, Diwali pamphlets. Very low value.

---

## Table 17: `erickshaw_sales`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| er_sale_id | INT | NO | Primary key | N |
| customer_id | INT | NO | FK → customers | N |
| employee_id | INT | NO | FK → employees (who handled the sale) | N |
| product_id | INT | NO | FK → products (e-rickshaw model SKU) | N |
| enquiry_date | DATE | YES | Initial enquiry date (may precede booking) | N |
| booking_date | DATE | NO | Booking/advance payment date | IS |
| delivery_date | DATE | YES | Actual delivery date | N |
| amount | DECIMAL(12,2) | NO | Sale amount (₹) | IS |
| cost_price | DECIMAL(12,2) | NO | Swastik's cost from OEM | IS |
| payment_method | ENUM | NO | `cash` / `upi` / `bank_transfer` | IS (large value → bank transfer common) |
| payment_status | ENUM | NO | `paid` / `pending` / `partial` | IS |
| er_model | VARCHAR(100) | NO | E-rickshaw model name (denormalized for quick query) | N |
| festive_occasion | VARCHAR(100) | YES | Festival name if sale coincided (e.g., "Akshaya Tritiya", "Diwali") — NULL otherwise | IS |

**Generator volume:** ~80–120 records over 39 months. Base rate: ~1 per 1–2 weeks. Festival spike: 2–3/week during Akshaya Tritiya (April/May) and Diwali/Navratri window.

---

## Table 18: `customer_feedback`

| Column | Type | Nullable | Description | Signal Type |
|---|---|---|---|---|
| feedback_id | INT | NO | Primary key | N |
| customer_id | INT | YES | FK → customers (NULL for anonymous) | N |
| sale_id | INT | YES | FK → sales (NULL for general feedback) | N |
| feedback_date | DATE | NO | Date of feedback | N |
| source | ENUM | NO | `in_store` / `whatsapp` / `google_maps` | N |
| rating | INT | NO | 1–5 star rating | IS (correlates with product quality and wait time) |
| review_text | TEXT | YES | Text review — English/Hinglish mix | IS (NLP target in Phase 6) |
| sentiment | ENUM | YES | `positive` / `neutral` / `negative` — filled by Phase 6 NLP | E |
| feedback_category | ENUM | YES | `product_quality` / `service` / `price` / `availability` | N |

---

## Table 19: `weather` *(External Reference — Generator Only)*

| Column | Type | Description | Signal Type |
|---|---|---|---|
| weather_id | INT | Primary key | N |
| date | DATE | Daily record | N |
| city | VARCHAR(50) | Ballia, UP | N |
| temperature_max | DECIMAL(5,2) | Max temp °C | REF |
| rainfall_mm | DECIMAL(7,2) | Daily rainfall mm | REF |
| season | ENUM | `pre_monsoon` / `monsoon` / `post_monsoon` / `winter` / `summer` | REF |
| is_extreme | BOOLEAN | Extreme weather event | REF |

**Correlation used:** Pre-monsoon (March–May) → ↑ exterior paint demand. During monsoon (June–September) → ↓ outdoor painting, ↓ exterior paint.

---

## Table 20: `fuel_prices` *(External Reference — Generator Only)*

| Column | Type | Description | Signal Type |
|---|---|---|---|
| fuel_price_id | INT | Primary key | N |
| date | DATE | Daily price record | N |
| petrol_price | DECIMAL(6,2) | Petrol price per litre in ₹ | REF |
| diesel_price | DECIMAL(6,2) | Diesel price per litre in ₹ | REF |

**Correlation used:** Rising petrol price → ↑ e-rickshaw enquiry and booking rate.

---

## Table 21: `inflation` *(External Reference — Generator Only)*

| Column | Type | Description | Signal Type |
|---|---|---|---|
| inflation_id | INT | Primary key | N |
| month | INT | Month (1–12) | N |
| year | INT | Year | N |
| cpi_index | DECIMAL(8,3) | CPI index value | REF |
| inflation_rate_pct | DECIMAL(5,2) | Month-on-month inflation % | REF |

**Correlation used:** Higher inflation → slight ↓ in basket size for retail customers; ↑ cost_price in `products` over time.

---

## Phase 3 Engineered Features

| Feature | Added To | Formula / Logic | ML Role |
|---|---|---|---|
| `clv` | customers | SUM(sales.total_amount) per customer_id | Input feature |
| `purchase_frequency` | customers | COUNT(sale_id) / months_since_first_purchase | Input feature |
| `recency_days` | customers | reference_date − MAX(sale_date) per customer | Input feature (churn model) |
| `avg_basket_size` | customers | AVG(sales.total_amount) per customer_id | Input feature |
| `repeat_customer_flag` | customers | COUNT(sales) > 1 → 1, else 0 | Input feature |
| `customer_segment` | customers | RFM-based: Champion / Loyal / At_Risk / Lost | Input feature |
| `festival_flag` | sales | sale_date falls in festival calendar → 1 | Input feature |
| `season` | sales | Derived from MONTH(sale_date) → pre_monsoon / monsoon / post_monsoon / winter | Input feature |
| `profit_pct` | sales_items | (unit_price × (1−discount_pct/100) − cost_price) / unit_price × 100 | **Target: Profit Prediction** |
| `return_flag` | sales | EXISTS(sales_returns for this sale_id) → 1 | **Target: Return Prediction** |
| `paint_price_index` | products | cost_price / cost_price_at_launch — tracks cost inflation per SKU | **Target: Price Prediction** |
| `inventory_turnover` | inventory | COGS / AVG(quantity_in_stock × cost_price) per period | BI / Reporting |
| `dead_stock_days` | inventory | Days since last movement per product | Input feature |
| `price_bucket` | products | Binned selling_price: Low (<₹200) / Mid (₹200–₹1000) / High (>₹1000) | Input feature |
| `festive_sale_flag` | erickshaw_sales | festive_occasion IS NOT NULL → 1 | Input feature |
| `delivery_lag_days` | erickshaw_sales | delivery_date − booking_date | Input feature |
