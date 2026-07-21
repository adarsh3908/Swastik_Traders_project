# Functional Requirement Specification (FRS)
## Swastik Traders — Retail Analytics Ecosystem

**Version:** 1.0
**Date:** July 2026
**Linked To:** BRD v1.0

---

## Overview

This document specifies what each phase's tooling **must do** — not how it does it, but what functional outcomes it must produce. It serves as a phase-by-phase acceptance checklist.

---

## Phase 1 — Synthetic Data Generation

| ID | Requirement |
|---|---|
| FRS-1.1 | Generator must produce CSV files for all 19 core tables defined in the BRD |
| FRS-1.2 | Data must span April 2023 – June 2026 (39 months) |
| FRS-1.3 | Paint sales must show a pre-monsoon spike and in-monsoon dip |
| FRS-1.4 | E-rickshaw sales must show inverse correlation with fuel prices |
| FRS-1.5 | Basket size must show slight downward pressure during high-inflation periods |
| FRS-1.6 | Sales/Inventory must reflect a warehouse capacity event in 2025 |
| FRS-1.7 | Every rule must include random noise — no hard cutoffs |
| FRS-1.8 | ~5% of records must contain deliberate data quality issues (missing values, bad phone formats, duplicate-like records, invalid GST) for Phase 3 cleaning |
| FRS-1.9 | Row counts must be documented and justified against BRD business scale |
| FRS-1.10 | Data Dictionary must be updated to mark each column as "generator-intentional signal" or "noise" |

---

## Phase 2 — Database Design

| ID | Requirement |
|---|---|
| FRS-2.1 | MySQL database must include all core tables from Phase 1 with matching column names/types |
| FRS-2.2 | All Primary Keys and Foreign Keys must be defined and enforced |
| FRS-2.3 | At minimum: NOT NULL on required fields, CHECK constraints on GST format and phone format |
| FRS-2.4 | Indexes must be defined on: all FK columns, date columns used in filters, customer_id, product_id |
| FRS-2.5 | Minimum 5 Views created for commonly joined datasets (e.g., vw_sales_full, vw_inventory_status) |
| FRS-2.6 | Minimum 2 Stored Procedures (e.g., sp_monthly_kpi, sp_supplier_performance) |
| FRS-2.7 | Minimum 1 Trigger (e.g., auto-update inventory on sales insert) |
| FRS-2.8 | Minimum 1 Event (e.g., nightly dead-inventory flag refresh) |
| FRS-2.9 | Schema must load all Phase 1 CSV data without FK violation errors |
| FRS-2.10 | 10–15 sample queries must run successfully against the loaded database |

---

## Phase 3 — ETL & Data Cleaning

| ID | Requirement |
|---|---|
| FRS-3.1 | All Phase 1 deliberate data quality issues must be detected and handled |
| FRS-3.2 | Missing value strategy must be documented per column (impute/flag/drop) |
| FRS-3.3 | Duplicate records must be removed with before/after counts logged |
| FRS-3.4 | Date validation: no sales before July 2022 (company founding), no delivery before sale date |
| FRS-3.5 | GST numbers must be validated against Indian GST format (15-character alphanumeric) |
| FRS-3.6 | Phone numbers must be validated (10-digit Indian mobile format) |
| FRS-3.7 | Product/brand names must be standardized to canonical form |
| FRS-3.8 | The following features must be engineered and stored: CLV, Purchase Frequency, Recency, Avg Basket Size, Festival Flag, Holiday Flag, Season, Profit %, Warehouse Expansion Flag, Inventory Turnover, Repeat Customer Flag, Price Bucket, Customer Segment (RFM), Delivery Delay |
| FRS-3.9 | No engineered feature used as ML input may be derived from the ML target (leakage check) |
| FRS-3.10 | Cleaning Report must include: % missing per table, dedup counts, validation failure rates |

---

## Phase 4 — SQL Business Analytics

| ID | Requirement |
|---|---|
| FRS-4.1 | Minimum 200 SQL queries, organized by category (Sales, Inventory, Revenue, Brand, Supplier, Warehouse, Customer, Seasonality, E-Rickshaw, Profitability) |
| FRS-4.2 | Each query must include: the business question it answers + one-line result interpretation |
| FRS-4.3 | Query complexity distribution: ~40% foundational, ~40% intermediate, ~20% advanced |
| FRS-4.4 | Must demonstrate: all JOIN types, window functions (RANK, ROW_NUMBER, LAG/LEAD), CTEs, stored procedures |
| FRS-4.5 | KPI queries (Revenue, Gross Profit %, Inventory Turnover) must be validated against Phase 5 dashboard numbers |
| FRS-4.6 | Dead inventory threshold must be explicitly defined (e.g., no movement in 90 days) and consistent across all phases |
| FRS-4.7 | ABC Analysis and RFM Analysis must each produce a classified output (A/B/C, High/Mid/Low segments) |

---

## Phase 5 — Power BI Dashboards

| ID | Requirement |
|---|---|
| FRS-5.1 | Star schema data model must be implemented (Fact + Dimension tables) |
| FRS-5.2 | A proper Date dimension table must be created (not Power BI auto date/time) |
| FRS-5.3 | All core KPIs must be implemented as explicit DAX measures (not calculated columns) |
| FRS-5.4 | Time intelligence (MTD, QTD, YTD) must be implemented via Calculation Groups |
| FRS-5.5 | Minimum 12 dashboard pages (see BRD Section 4 entity list for scope) |
| FRS-5.6 | Executive Dashboard must be the most polished — used as the presentation flagship |
| FRS-5.7 | Row Level Security must be configured (e.g., warehouse-level role) |
| FRS-5.8 | Bookmarks, Drill-through, and Tooltips must be demonstrated in at least 3 dashboards |
| FRS-5.9 | Field Parameters must be used for dynamic measure switching |
| FRS-5.10 | All KPI numbers must cross-check against Phase 4 SQL results (no divergence >1% on aggregates) |
| FRS-5.11 | Forecast Dashboard must not be built until Phase 6 time series models are finalized |
| FRS-5.12 | Published to Power BI Service (workspace link required) |

---

## Phase 6 — Machine Learning

| ID | Requirement |
|---|---|
| FRS-6.1 | 13 total models: 3 deep-dive + 10 regular |
| FRS-6.2 | Deep Model 1 — Profit Prediction: must compare ≥3 algorithms, include hyperparameter tuning, feature importance, and business recommendation |
| FRS-6.3 | Deep Model 2 — Wholesale Paint Price Prediction: must include EDA, feature selection justification, and error analysis |
| FRS-6.4 | Deep Model 3 — Product Return Prediction: must handle class imbalance explicitly, use appropriate metrics (F1, ROC-AUC, not just accuracy) |
| FRS-6.5 | Train/test split must respect time order for any forecasting model (no future leakage) |
| FRS-6.6 | Leakage checklist must be completed and documented for all 3 deep models |
| FRS-6.7 | Each model must produce a saved model artifact (.pkl or equivalent) |
| FRS-6.8 | Google Review Sentiment model output must feed into the Power BI Review Dashboard |
| FRS-6.9 | Time series forecast output must feed into the Power BI Forecast Dashboard |
| FRS-6.10 | Regular models must each include: problem statement, light EDA, evaluation metrics, one-paragraph business interpretation |

---

## Phase 7 — Deployment

| ID | Requirement |
|---|---|
| FRS-7.1 | 3 deep ML models must each have a deployed Streamlit or Gradio demo app |
| FRS-7.2 | All demo apps must be hosted on HuggingFace Spaces or Render (publicly accessible URL) |
| FRS-7.3 | MySQL database must be containerized in Docker with a working docker-compose setup |
| FRS-7.4 | Docker setup must include schema creation + seed data load in a single command |
| FRS-7.5 | GitHub Pages site must link to all 13 repositories, Power BI workspace, and ML demo apps |
| FRS-7.6 | All deployed URLs must be tested fresh before Phase 8 begins |

---

## Phase 8 — Reports

| ID | Requirement |
|---|---|
| FRS-8.1 | SQL Report: 40–60 pages, structured by business question category |
| FRS-8.2 | Power BI Report: dashboard screenshots + 3–5 bullet insights per dashboard |
| FRS-8.3 | ML Report: per-model sections for all 3 deep models; combined summary for 10 regular |
| FRS-8.4 | Final Business Report: 100–150 pages, must include Executive Summary written last |
| FRS-8.5 | Every number quoted in Final Report must trace back to a SQL query or dashboard visual |
| FRS-8.6 | Business Recommendations section must contain specific, numbered, actionable items |
| FRS-8.7 | Known Limitations section must be included in Executive Summary |
| FRS-8.8 | Future Scope section must frame unbuilt items as intentional scoping, not gaps |

---

## Phase 9 — Presentation

| ID | Requirement |
|---|---|
| FRS-9.1 | 25–35 slides, exported as both .pptx and PDF |
| FRS-9.2 | Every slide must have a "so what?" — chart alone is insufficient |
| FRS-9.3 | Dashboard screenshots must be reused directly from Phase 5 (no recreation) |
| FRS-9.4 | Q&A preparation: all team members must be able to present any slide, not just their own |
| FRS-9.5 | Deck must be tested for actual time length before presentation day |

---

## Phase 10 — GitHub Structure

| ID | Requirement |
|---|---|
| FRS-10.1 | 13 repositories created under one GitHub organization/account |
| FRS-10.2 | Every repository must have a README meeting the standard in 10-Github-Structure.md |
| FRS-10.3 | 13-Project-Documentation is the single link shared with evaluators |
| FRS-10.4 | No repository may be empty or placeholder-only at submission |
| FRS-10.5 | Consistent naming convention across all repos (kebab-case, numbered prefix) |
