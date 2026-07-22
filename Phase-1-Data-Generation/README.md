# Phase 1 — Synthetic Data Generation

## Overview
Generates 21 CSV files representing ~3 years of synthetic business data
for **Swastik Traders**, a paint + e-rickshaw retail shop in Ballia, UP.

**Data range:** April 2023 – June 2026 (39 months)
**Total rows:** ~35,851 across all tables

---

## How to Run

```bash
# From this directory:
pip install faker pandas numpy   # one-time
python generate_data.py
```

Output goes to `data/raw/`.

---

## Output Files

| File | Rows | Notes |
|---|---|---|
| `weather.csv` | 1,461 | Daily Ballia weather, Jul 2022–Jun 2026 |
| `fuel_prices.csv` | 1,461 | Daily petrol/diesel prices |
| `inflation.csv` | 54 | Monthly CPI index |
| `product_categories.csv` | 11 | Hierarchy: Paint → Interior/Exterior/Primer/Putty |
| `brands.csv` | 5 | Asian Paints, Indigo, JSW, Saarthi, City Life |
| `products.csv` | 202 | All SKUs (Brand × Product × Color × Size) |
| `suppliers.csv` | 11 | Paint distributors + e-rickshaw OEMs + accessory wholesalers |
| `warehouses.csv` | 2 | Godown 1 + Godown 2 |
| `employees.csv` | 7 | 1 owner, 2 co-founders, 4 labourers |
| `promotions.csv` | 19 | Festival + seasonal campaigns |
| `customers.csv` | 950 | Retail + contractor + painter customers |
| `inventory.csv` | 401 | Product × Godown snapshot |
| `purchases.csv` | 83 | Supplier procurement events |
| `purchase_orders.csv` | 479 | Line items per procurement |
| `sales.csv` | 6,865 | In-store transactions |
| `sales_items.csv` | 15,245 | Line items per sale |
| `payments.csv` | 6,865 | cash / UPI / bank_transfer |
| `sales_returns.csv` | 103 | ~1.5% return rate |
| `erickshaw_sales.csv` | 141 | ~1/fortnight base + festival spikes |
| `expenses.csv` | 113 | Salary, utilities, maintenance, marketing, one-time setup |
| `customer_feedback.csv` | 1,373 | In-store + WhatsApp + Google Maps reviews |

---

## Correlations Encoded

| Signal | Effect |
|---|---|
| Pre-monsoon (Mar–May) | Exterior paint sales × 1.35 |
| Monsoon (Jun–Sep) | All paint sales × 0.70 |
| Festival dates (Diwali, Navratri) | Sales × 1.8 |
| Akshaya Tritiya | E-rickshaw bookings: ~2–3/week for 2 weeks |
| Fuel price ↑ (2-week lag) | E-rickshaw probability ↑ |
| 2025 Godown 2 expansion | Warehouse 2 active from Feb 2025 |
| Putty | Volume rank #1 (37,000+ units), margin rank last (7%) |
| Accessories (brushes/rollers) | Volume rank lower, margin 34–35% |

---

## Dirty Data Injected

| Issue | Table | Rate |
|---|---|---|
| Malformed phone numbers | customers | ~3.8% |
| Missing address | customers | ~7.7% |
| Product name inconsistencies | products | ~5% |
| Missing actual_delivery_date | purchase_orders | ~5% |
| Quantity received < ordered | purchase_orders | ~8% |

> These issues are intentional. Phase 3 (ETL & Cleaning) will document and fix them.

---

## Next Phase

→ **Phase 2:** MySQL schema creation and bulk data load from CSVs.
