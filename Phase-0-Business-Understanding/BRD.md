# Business Requirement Document (BRD)
## Swastik Traders — Retail Analytics Ecosystem

**Version:** 2.0 (Updated with ground-truth business corrections)
**Date:** July 2026
**Status:** Approved

---

## 1. Company Overview

| Field | Details |
|---|---|
| **Company Name** | Swastik Traders |
| **Founded** | Mid-2022 |
| **Location** | Ballia, Uttar Pradesh, India |
| **Business Type** | Single-outlet paint & hardware retail shop with e-rickshaw dealership |
| **Shop Structure** | 1 main shop + Godown 1 + Godown 2 (both godowns physically attached to shop) |
| **Property** | Owned (no rent). One-time setup cost ~₹10 Lakh. |
| **Primary Product Lines** | Paints (bulk batches + individual tubs/buckets), Hardware/accessories, E-Rickshaws |
| **Paint Brands Stocked** | Asian Paints, Indigo Paints, JSW Paints |
| **E-Rickshaw Brand** | Saarthi / City Life (regional UP brands) |
| **Employees** | 7 total: 1 Owner, 2 Co-founders, 4 Labourers |

---

## 2. Business Backstory

Swastik Traders was founded in mid-2022 in Ballia, Uttar Pradesh by two co-founders with a background in construction material supply. The business opened as a **multi-brand paint retail shop** — stocking Asian Paints, Indigo Paints, and JSW Paints, serving both bulk buyers (local painters, contractors, small-scale builders) and walk-in retail customers buying 1–2 buckets with brushes.

Within six months (late 2022), the owner identified rising demand for e-rickshaws among local last-mile transport operators and small contractors — driven by UP's EV push and escalating petrol prices. An e-rickshaw dealership desk was added, selling regional brands (Saarthi, City Life) on a **very low frequency basis** — roughly 1 unit per week or per fortnight under normal conditions, spiking to 2–3 per week during auspicious occasions like **Akshaya Tritiya** and major festive seasons (Diwali, Navratri).

By 2025, growing inventory volumes led the team to formalize and expand their storage — **Godown 2 capacity was operationalized fully**, effectively doubling the usable storage.

**Sales model:**
- **All sales are in-store only** — no B2B selling contracts, no online, no dealer distribution from Swastik's side.
- Customers are **regular individuals**: local painters, homeowners, small contractors buying for personal projects.
- Some customers buy in bulk (20L drums, multiple bags of putty), others buy 1–2 buckets with a brush.
- **Procurement is B2B** — Swastik buys from brand distributors/representatives who deliver to the shop/godowns directly.

**Why paint & hardware together:** Standard in Indian regional retail. Paint brushes, rollers, putty blades, masking tape, and thinner are naturally co-purchased with paint. Higher margins on accessories vs. commodity paints.

**Note on putty:** Putty (especially Asian Paints Wall Care Putty) is the **highest volume, lowest margin** product — sells in very high quantity but barely moves the gross profit needle. This is a key insight for the primary KPI.

---

## 3. Primary KPI (North-Star Metric)

> **Maximize Gross Profit %**
>
> Gross Profit % = (Revenue − Cost of Goods Sold) / Revenue × 100

Every SQL analysis, dashboard visual, and ML model in this project is designed to **measure, explain, or improve gross margin**. Given that putty is high-volume/low-margin and accessories are low-volume/high-margin, product-mix analysis becomes central to this KPI.

---

## 4. Core Entities & Tables

| Entity | Table Name | Description |
|---|---|---|
| Customers | `customers` | Individual buyers — homeowners, painters, contractors |
| Products | `products` | Paint SKUs (brand × product × size), accessories, e-rickshaw models |
| Product Categories | `product_categories` | Interior Paint / Exterior Paint / Primer / Putty / Enamel / Accessory / E-Rickshaw |
| Brands | `brands` | Asian Paints, Indigo Paints, JSW Paints, Saarthi/City Life (e-rickshaw) |
| Suppliers | `suppliers` | All external parties: brand distributors, accessory wholesalers, e-rickshaw OEM reps (merged) |
| Warehouses | `warehouses` | Godown 1 + Godown 2 (both attached to main shop) |
| Inventory | `inventory` | Stock levels per godown per product |
| Purchases | `purchases` | Procurement from suppliers (header) |
| Purchase Orders | `purchase_orders` | Line-item detail per product per procurement |
| Sales | `sales` | Customer purchase transactions (header, all in-store) |
| Sales Items | `sales_items` | Line items per sale (product, qty, price, margin) |
| Sales Returns | `sales_returns` | Returns — very rare; tracked for completeness |
| Payments | `payments` | Payment records: cash / UPI / bank transfer only |
| Employees | `employees` | 7 staff: 1 owner, 2 co-founders, 4 labourers |
| Expenses | `expenses` | Operating costs: salary, utilities, maintenance, marketing (no rent) |
| E-Rickshaw Sales | `erickshaw_sales` | Separate lifecycle: enquiry → booking → delivery |
| Customer Feedback | `customer_feedback` | All feedback: in-store word-of-mouth, WhatsApp, Google Maps reviews (merged) |
| Promotions | `promotions` | Festival/seasonal discount campaigns |
| Weather | `weather` | External reference — drives paint demand seasonality (generator only) |
| Fuel Prices | `fuel_prices` | External reference — drives e-rickshaw demand (generator only) |
| Inflation | `inflation` | External reference — drives basket size / price sensitivity (generator only) |

**Note on Suppliers (Merged):** All external parties (paint brand distributors, accessory wholesalers, e-rickshaw OEM reps) are in a single `suppliers` table with `supplier_type` column.

**Note on Customer Feedback (Merged):** In-store feedback, WhatsApp messages, and Google Maps review simulations are in one `customer_feedback` table with a `source` column.

**Note on External Factor Tables:** `weather`, `fuel_prices`, and `inflation` are **reference/staging tables used solely to drive realistic correlations in the synthetic data generator**. They are not part of the core transactional schema.

**Logistics note:** Delivery is not a formal business concern. Suppliers deliver directly to the shop/godowns. Customers either carry purchases themselves or Swastik's labourers help with loading. No third-party delivery or formal dispatch tracking is needed. The `logistics` table is **dropped** from the schema.

---

## 5. Product Catalogue (Representative — used for data generation)

> **SKU structure:** Each `product_id` = Brand × Product Name × **Color** × Pack Size.
> Color variants apply to emulsions, exterior paints, enamel, and distemper.
> **Primers and putty are White/Standard only** — no tinting.

### Interior Paints

| Brand | Product Name | Color | Sizes Available |
|---|---|---|---|
| Asian Paints | Tractor Emulsion | White | 1L, 4L, 10L, 20L |
| Asian Paints | Tractor Emulsion | Ivory | 1L, 4L, 10L, 20L |
| Asian Paints | Tractor Emulsion | Cream | 1L, 4L, 10L, 20L |
| Asian Paints | Royale Shyne | White | 1L, 4L, 10L, 20L |
| Asian Paints | Royale Shyne | Ivory | 1L, 4L, 10L, 20L |
| Asian Paints | Royale Shyne | Cream | 1L, 4L, 10L, 20L |
| Asian Paints | Apcolite Premium Emulsion | White | 1L, 4L, 10L, 20L |
| Asian Paints | Apcolite Premium Emulsion | Ivory | 1L, 4L, 10L, 20L |
| Asian Paints | Apcolite Premium Emulsion | Cream | 1L, 4L, 10L, 20L |
| Indigo Paints | Infinity Interior Emulsion | White | 1L, 4L, 10L, 20L |
| Indigo Paints | Infinity Interior Emulsion | Ivory | 1L, 4L, 10L, 20L |
| Indigo Paints | Infinity Interior Emulsion | Cream | 1L, 4L, 10L, 20L |
| Indigo Paints | Plasto Emulsion Plus | White | 1L, 4L, 10L, 20L |
| Indigo Paints | Plasto Emulsion Plus | Ivory | 1L, 4L, 10L, 20L |
| Indigo Paints | Plasto Emulsion Plus | Cream | 1L, 4L, 10L, 20L |
| JSW Paints | Joie Interior Emulsion | White | 1L, 4L, 10L, 20L |
| JSW Paints | Joie Interior Emulsion | Ivory | 1L, 4L, 10L, 20L |
| JSW Paints | Joie Interior Emulsion | Cream | 1L, 4L, 10L, 20L |

### Exterior Paints

| Brand | Product Name | Color | Sizes Available |
|---|---|---|---|
| Asian Paints | Apex Exterior | White | 1L, 4L, 10L, 20L |
| Asian Paints | Apex Exterior | Ivory | 1L, 4L, 10L, 20L |
| Asian Paints | Apex Exterior | Cream | 1L, 4L, 10L, 20L |
| Asian Paints | Apex Ultima | White | 1L, 4L, 10L, 20L |
| Asian Paints | Apex Ultima | Ivory | 1L, 4L, 10L, 20L |
| Asian Paints | Apex Ultima | Cream | 1L, 4L, 10L, 20L |
| Asian Paints | Ace Exterior | White | 4L, 10L, 20L |
| Asian Paints | Ace Exterior | Ivory | 4L, 10L, 20L |
| Asian Paints | Ace Exterior | Cream | 4L, 10L, 20L |
| Indigo Paints | Elastomeric Exterior Emulsion | White | 4L, 10L, 20L |
| Indigo Paints | Elastomeric Exterior Emulsion | Ivory | 4L, 10L, 20L |
| Indigo Paints | Elastomeric Exterior Emulsion | Cream | 4L, 10L, 20L |
| Indigo Paints | All Season Exterior Emulsion | White | 4L, 10L, 20L |
| Indigo Paints | All Season Exterior Emulsion | Ivory | 4L, 10L, 20L |
| Indigo Paints | All Season Exterior Emulsion | Cream | 4L, 10L, 20L |
| JSW Paints | Joie Exterior Emulsion | White | 4L, 10L, 20L |
| JSW Paints | Joie Exterior Emulsion | Ivory | 4L, 10L, 20L |
| JSW Paints | Joie Exterior Emulsion | Cream | 4L, 10L, 20L |

### Enamel & Distemper

| Brand | Product Name | Color | Sizes Available |
|---|---|---|---|
| Asian Paints | Apcolite Enamel (Gloss) | White | 500ml, 1L, 4L |
| Asian Paints | Apcolite Enamel (Gloss) | Ivory | 500ml, 1L, 4L |
| Asian Paints | Apcolite Enamel (Gloss) | Cream | 500ml, 1L, 4L |
| Asian Paints | Tractor Synthetic Distemper | White | 5kg, 10kg, 20kg |
| Asian Paints | Tractor Synthetic Distemper | Ivory | 5kg, 10kg, 20kg |
| Asian Paints | Tractor Synthetic Distemper | Light Yellow | 5kg, 10kg, 20kg |

### Primers — White Only

| Brand | Product Name | Color | Sizes Available |
|---|---|---|---|
| Asian Paints | Wall Primer (WB) | White | 4L, 10L, 20L |
| Asian Paints | Exterior Wall Primer | White | 4L, 10L, 20L |
| Indigo Paints | Exterior Wall Primer | White | 4L, 10L, 20L |
| Indigo Paints | Water Thinnable Cement Primer | White | 4L, 10L, 20L |
| JSW Paints | Joie Primer (Interior) | White | 4L, 10L |
| JSW Paints | Joie Primer (Exterior) | White | 4L, 10L |

### Putty — White Only

| Brand | Product Name | Color | Sizes Available |
|---|---|---|---|
| Asian Paints | TruCare Wall Care Putty | White | 5kg, 10kg, 20kg, 40kg |
| Indigo Paints | Polymer Putty | White | 10kg, 20kg, 40kg |
| Indigo Paints | Acrylic Wall Putty | White | 1kg pouch, 10kg, 20kg |
| JSW Paints | Acrylic Wall Putty | White | 10kg, 20kg |
| JSW Paints | Cement Putty | White | 10kg, 20kg |

> **Total paint SKUs:** Colour products ~147 + White-only ~33 = **~180 SKUs**

### Hardware / Accessories (no color variants)

| Product | Sizes / Variants |
|---|---|
| Paint Brush | 1 inch, 2 inch, 3 inch, 4 inch |
| Paint Roller | 4 inch, 6 inch, 9 inch |
| Roller Tray | Standard |
| Masking Tape | 1 inch, 2 inch |
| Turpentine / Thinner | 500ml, 1L |
| Putty Blade / Scraper | Small, Medium, Large |
| Sandpaper | 60 grit, 100 grit, 180 grit |
| Paint Stirrer | Standard |

### E-Rickshaw Models

| Brand | Model | Type |
|---|---|---|
| Saarthi | Saarthi Standard | Passenger (4-seater) |
| Saarthi | Saarthi Plus | Passenger (5-seater) |
| City Life | City Life Mini | Passenger (4-seater) |

---
## 6. KPIs to Track

| KPI | Notes |
|---|---|
| **Gross Profit %** ⭐ | Primary KPI. Track by product, category, brand, month |
| Revenue (daily / monthly / quarterly / yearly) | Volume tracking |
| Gross Profit by Category | Putty will show high volume / low margin contrast |
| Gross Profit by Brand | Asian Paints vs. Indigo vs. JSW margin comparison |
| Inventory Turnover | COGS / Avg inventory — putty will top this |
| Dead Inventory Value | Stock > 90 days with no movement |
| Customer Repeat Rate | % customers returning |
| Average Basket Size | Value per transaction |
| E-Rickshaw Revenue Contribution | Small % of total, but high margin per unit |
| Supplier On-Time Delivery % | Brand distributors' reliability |
| Monthly Expense vs. Revenue | Operating cost as % of revenue |
| Target Achievement | Actual vs. planned monthly revenue |
| Promotion Effectiveness | Revenue lift during festival campaigns |

**Removed KPIs:** Warehouse Utilization (2 attached godowns, not a business concern), Order Fulfillment Delay (logistics not tracked).

---

## 7. Business Questions Bank

### Sales & Revenue
- Which product categories drive the most revenue vs. most gross profit?
- What is the monthly/quarterly revenue trend across 2023–2026?
- Which paint brand contributes the most to gross margin?
- Does festival/promotion timing improve gross profit % or just volume?

### Product & Margin
- Which products have the highest gross margin %?
- Which products are high-volume but low-margin (putty effect)?
- What is the optimal product mix to maximize overall gross profit %?
- Which size SKUs (1L vs 20L) have better margin profiles?

### Inventory
- Which products are dead inventory candidates (no movement in 90+ days)?
- What is inventory turnover by category?
- Which products frequently go out of stock?

### Customers
- What is the RFM segmentation of Swastik's customer base?
- Who are the repeat customers and what do they buy?
- What is the average basket size by customer type?

### Suppliers
- Which brand distributors have the best on-time delivery record?
- Does procurement timing affect margin (buying before price hike)?

### E-Rickshaw
- Is e-rickshaw sales volume correlated with fuel prices?
- What is e-rickshaw's gross margin contribution per unit vs. annual total?
- Do festive season spikes in e-rickshaw sales match auspicious calendar dates?

### Expenses
- What is the monthly operating cost breakdown (salary vs. utilities vs. maintenance vs. marketing)?
- What is the expense-to-revenue ratio trend?

---

## 8. Scope

### In-Scope
- Synthetic data generation for April 2023 – June 2026
- MySQL relational database
- Python ETL pipeline with feature engineering
- 200+ SQL business analytics queries
- Power BI dashboards
- 13 ML models (3 deep + 10 regular)
- Deployment (Streamlit apps + Docker + GitHub Pages)
- Reports and Presentation

### Out-of-Scope
- Real customer data (all data is synthetic)
- Online sales channel (in-store only)
- B2B sales contracts (Swastik is the buyer in B2B, not the seller)
- Delivery / logistics tracking (not a business concern)
- Rent expense (property is owned)
- Credit or cheque payments (cash / UPI / bank transfer only)
- Warehouse utilization dashboards (godowns are attached, not a managed concern)

---

## 9. Known Limitations

1. **Synthetic data risk:** All data is AI-generated. Generator uses noise and confounders to reduce circularity, but ML models may reflect generator patterns rather than true business relationships.
2. **E-rickshaw sample size:** ~1 sale/week or fortnight means very few e-rickshaw records over 39 months (~80–100 total). ML models on e-rickshaw data will have limited statistical power — acknowledged in Final Report.
3. **Single location:** Ballia, UP-specific patterns. Not generalizable.
4. **External factor tables:** Weather, fuel prices, inflation are synthetic approximations, not real historical data.
5. **Putty volume distortion:** High putty volume will skew pure revenue metrics. All analyses must control for margin alongside volume.

---

## 10. Team & Contribution Notes

| Phase | Owner | Reviewer |
|---|---|---|
| Phase 0 — Business Planning | TBD | TBD |
| Phase 1 — Data Generation | TBD | TBD |
| Phase 2 — Database Design | TBD | TBD |
| Phase 3 — ETL & Cleaning | TBD | TBD |
| Phase 4 — SQL Analytics | TBD | TBD |
| Phase 5 — Power BI | TBD | TBD |
| Phase 6 — ML | TBD | TBD |
| Phase 7 — Deployment | TBD | TBD |
| Phase 8 — Reports | TBD | TBD |
| Phase 9 — Presentation | TBD | TBD |
