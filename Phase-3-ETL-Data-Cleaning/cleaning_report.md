# Data Cleaning & ETL Execution Report

## 1. Overview
This report documents the metrics, validation outcomes, and details of the Phase 3 ETL pipeline.

## 2. Table Cleaning Summary

| Table | Before Rows | After Rows | Issues Handled | Detail |
|---|---|---|---|---|
| `customers` | 950 | 950 | 73 missing addresses, 36 malformed phones | Imputed missing addresses to 'Not Provided'; validated phone formats and flagged invalid numbers |
| `products` | 202 | 202 | 9 name inconsistencies | Standardized brand naming prefixes; categorized price buckets and estimated paint coverages |
| `suppliers` | 11 | 11 | 11 masked numbers | Normalized 'XXXXXX' phone masks to '000000' |
| `sales` | 6865 | 6865 | 0 double-billed items | Removed duplicate transactions based on customer, date, and amount |
| `purchase_orders` | 479 | 479 | 0 delivery date anomalies | Adjusted delivery dates that occurred before purchase orders; calculated delay metrics and logged 40 order shortfalls |

## 3. Feature Engineering Log

The following domain-specific features were successfully calculated and appended to the dataset:

- **Customer Lifetime Value (CLV)**: Cumulative gross profit across both paint and e-rickshaw sales per customer.
- **RFM Segmentation**: Categorized customers into *Champions, Loyal Customers, Promising, Need Attention, Lost* segments using Recency, Frequency, and Monetary scoring.
- **Seasonality & Context Flags**: Appended `festival_flag`, `holiday_flag`, `season` (`pre_monsoon`, `monsoon`, etc.), and `warehouse_expansion_flag` to sales.
- **Price Bucketing**: Products binned into *Low, Medium, High* buckets using selling price quantiles.
- **Paint Coverage Estimate**: Domain-specific estimation of coverage in sq ft per SKU based on pack size and paint type.
- **Delivery Timeliness**: Calculated delay metrics (expected vs. actual delivery date) for all purchase orders.

Report generated successfully on: 2026-07-23 13:21:00
