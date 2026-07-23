import os
import pandas as pd
import numpy as np
from datetime import datetime, date

# Input and Output paths
RAW_DIR = r"c:\Users\hawka\Swastik_Traders_project\Phase-1-Data-Generation\data\raw"
CLEAN_DIR = r"c:\Users\hawka\Swastik_Traders_project\Phase-3-ETL-Data-Cleaning\cleaned_csv"
os.makedirs(CLEAN_DIR, exist_ok=True)

# Reference End Date for Recency calculation (dataset ends 2026-06-30)
MAX_DATE = date(2026, 6, 30)

# Festival calendar from Phase 1
FESTIVALS = {
    "Holi":             [date(2023,3,8),  date(2024,3,25), date(2025,3,14), date(2026,3,25)],
    "Akshaya Tritiya":  [date(2023,4,22), date(2024,5,10), date(2025,4,30), date(2026,5,14)],
    "Navratri":         [date(2023,10,15),date(2024,10,3), date(2025,9,22)],
    "Diwali":           [date(2023,11,12),date(2024,11,1), date(2025,10,20)],
    "Chhath Puja":      [date(2023,11,19),date(2024,11,7), date(2025,10,27)]
}

# Indian Public Holidays
PUBLIC_HOLIDAYS = [
    # Fixed date holidays (Month, Day)
    (1, 26),   # Republic Day
    (8, 15),   # Independence Day
    (10, 2),   # Gandhi Jayanti
    (12, 25)   # Christmas
]

# Track statistics for report
report_stats = {
    "customers": {"before_rows": 0, "after_rows": 0, "missing_handled": 0, "invalid_phones": 0},
    "products": {"before_rows": 0, "after_rows": 0, "name_normalizations": 0},
    "suppliers": {"before_rows": 0, "after_rows": 0, "phone_normalizations": 0},
    "sales": {"before_rows": 0, "after_rows": 0, "duplicates_removed": 0},
    "purchase_orders": {"before_rows": 0, "after_rows": 0, "date_fixes": 0, "shortfalls": 0}
}

# ── Helper Functions ──────────────────────────────────────────
def is_festival_date(d):
    if d is None:
        return 0
    # convert pd.Timestamp to date if needed
    if isinstance(d, pd.Timestamp):
        d = d.date()
    elif isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    for name, dates in FESTIVALS.items():
        for fd in dates:
            if abs((d - fd).days) <= 7:
                return 1
    return 0

def is_holiday_date(d):
    if d is None:
        return 0
    if isinstance(d, pd.Timestamp):
        d = d.date()
    elif isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    for m, day in PUBLIC_HOLIDAYS:
        if d.month == m and d.day == day:
            return 1
    return 0

def get_season(d):
    if d is None:
        return "unknown"
    if isinstance(d, pd.Timestamp):
        d = d.date()
    elif isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    m = d.month
    if m in [3, 4, 5]:
        return "pre_monsoon"
    elif m in [6, 7, 8, 9]:
        return "monsoon"
    elif m in [11, 12, 1, 2]:
        return "winter"
    else:
        return "post_monsoon"

# ── 1. Clean Dimension Tables ─────────────────────────────────

print("Cleaning Customers...")
cust_df = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
report_stats["customers"]["before_rows"] = len(cust_df)

# Address: Fill missing with "Not Provided"
report_stats["customers"]["missing_handled"] = cust_df["address"].isna().sum()
cust_df["address"] = cust_df["address"].fillna("Not Provided")

# Phone Number Cleaning: Strip non-numeric, validate Indian mobile number (10 digits starting with 6-9)
def clean_phone(phone):
    if pd.isna(phone):
        return None, 0
    p_str = "".join(filter(str.isdigit, str(phone)))
    if len(p_str) == 10 and p_str[0] in "6789":
        return p_str, 1
    else:
        return p_str, 0 # Keep the digits but flag as invalid

cleaned_phones = [clean_phone(p) for p in cust_df["phone"]]
cust_df["phone"] = [cp[0] for cp in cleaned_phones]
cust_df["is_valid_phone"] = [cp[1] for cp in cleaned_phones]
report_stats["customers"]["invalid_phones"] = len(cust_df[cust_df["is_valid_phone"] == 0])
report_stats["customers"]["after_rows"] = len(cust_df)


print("Cleaning Brands & Categories...")
brand_df = pd.read_csv(os.path.join(RAW_DIR, "brands.csv"))
cat_df = pd.read_csv(os.path.join(RAW_DIR, "product_categories.csv"))


print("Cleaning Suppliers...")
sup_df = pd.read_csv(os.path.join(RAW_DIR, "suppliers.csv"))
report_stats["suppliers"]["before_rows"] = len(sup_df)
# Replace phone mask pattern "XXXXXX" with "000000" and flag
def clean_supplier_phone(p):
    if pd.isna(p): return None
    p_str = str(p).replace("XXXXXX", "000000")
    return p_str

sup_df["phone"] = sup_df["phone"].apply(clean_supplier_phone)
report_stats["suppliers"]["phone_normalizations"] = sup_df["phone"].str.contains("000000").sum()
report_stats["suppliers"]["after_rows"] = len(sup_df)


print("Cleaning Warehouses & Employees...")
wh_df = pd.read_csv(os.path.join(RAW_DIR, "warehouses.csv"))
emp_df = pd.read_csv(os.path.join(RAW_DIR, "employees.csv"))


print("Cleaning Products...")
prod_df = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
report_stats["products"]["before_rows"] = len(prod_df)

# Standardize product names: "asian paints ltd" -> "Asian Paints", "Indigo Paint" -> "Indigo Paints"
def standardize_prod_name(name):
    if pd.isna(name): return name
    cleaned = str(name).strip()
    # Normalize Asian Paints
    if cleaned.lower().startswith("asian paints ltd"):
        cleaned = "Asian Paints" + cleaned[16:]
    elif cleaned.lower().startswith("asian paints"):
        cleaned = "Asian Paints" + cleaned[12:]
    # Normalize Indigo Paints
    if cleaned.lower().startswith("indigo paint "):
        cleaned = "Indigo Paints " + cleaned[13:]
    elif cleaned.lower().startswith("indigo paints"):
        cleaned = "Indigo Paints" + cleaned[13:]
    # Normalize JSW
    if cleaned.lower().startswith("jsw paint "):
        cleaned = "JSW Paints " + cleaned[10:]
    elif cleaned.lower().startswith("jsw paints"):
        cleaned = "JSW Paints" + cleaned[10:]
        
    return cleaned

cleaned_names = prod_df["product_name"].apply(standardize_prod_name)
report_stats["products"]["name_normalizations"] = (prod_df["product_name"] != cleaned_names).sum()
prod_df["product_name"] = cleaned_names

# Product Feature Engineering: Price Bucket (Quantiles: Low <= 33%, Med 33-66%, High > 66%)
prod_df["price_bucket"] = pd.qcut(prod_df["selling_price"], q=3, labels=["Low", "Medium", "High"])

# Product Feature Engineering: Paint Coverage Estimate (litres or kg)
# Emulsion paints cover ~100 sq ft per litre. Putty covers ~15 sq ft per kg. Accessories cover 0.
def estimate_coverage(row):
    cat_id = row["category_id"]
    size_str = str(row["pack_size"])
    # extract numeric size
    num_part = "".join(c for c in size_str if c.isdigit() or c == '.')
    try:
        size_val = float(num_part) if num_part else 1.0
    except ValueError:
        size_val = 1.0
        
    if cat_id == 5: # Putty (kg)
        return size_val * 15.0 # sq ft
    elif cat_id in [2, 3, 4, 6]: # Paints/Primers (litres)
        return size_val * 100.0 # sq ft
    else: # Accessories, E-rickshaws
        return 0.0

prod_df["paint_coverage_sqft_estimate"] = prod_df.apply(estimate_coverage, axis=1)
report_stats["products"]["after_rows"] = len(prod_df)


# ── 2. Clean Fact Tables & Perform Feature Engineering ───────────

print("Cleaning Sales & Payments...")
sales_df = pd.read_csv(os.path.join(RAW_DIR, "sales.csv"))
sitems_df = pd.read_csv(os.path.join(RAW_DIR, "sales_items.csv"))
pay_df = pd.read_csv(os.path.join(RAW_DIR, "payments.csv"))

report_stats["sales"]["before_rows"] = len(sales_df)

# Deduplicate Sales based on (customer_id, sale_date, total_amount) to catch double billing
sales_dates = pd.to_datetime(sales_df["sale_date"])
duplicates = sales_df.duplicated(subset=["customer_id", "sale_date", "total_amount"], keep='first')
report_stats["sales"]["duplicates_removed"] = duplicates.sum()
sales_df = sales_df[~duplicates]

# Keep only sales items and payments that belong to valid sales
sitems_df = sitems_df[sitems_df["sale_id"].isin(sales_df["sale_id"])]
pay_df = pay_df[pay_df["sale_id"].isin(sales_df["sale_id"])]

# Date parsing
sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
pay_df["payment_date"] = pd.to_datetime(pay_df["payment_date"])

# Date sequence check: payment_date >= sale_date
pay_df = pay_df.merge(sales_df[["sale_id", "sale_date"]], on="sale_id", how="left")
pay_df["payment_date"] = np.where(pay_df["payment_date"] < pay_df["sale_date"], pay_df["sale_date"], pay_df["payment_date"])
pay_df = pay_df.drop(columns=["sale_date"])

# Sales Feature Engineering: Festival_Flag, Holiday_Flag, Season, Warehouse_Expansion_Flag
sales_df["festival_flag"] = sales_df["sale_date"].apply(is_festival_date)
sales_df["holiday_flag"] = sales_df["sale_date"].apply(is_holiday_date)
sales_df["season"] = sales_df["sale_date"].apply(get_season)
sales_df["warehouse_expansion_flag"] = np.where(sales_df["sale_date"] >= pd.Timestamp("2025-02-01"), 1, 0)
report_stats["sales"]["after_rows"] = len(sales_df)


print("Cleaning Sales Returns...")
sret_df = pd.read_csv(os.path.join(RAW_DIR, "sales_returns.csv"))
sret_df["return_date"] = pd.to_datetime(sret_df["return_date"])
# Ensure returns belong to active sales
sret_df = sret_df[sret_df["sale_id"].isin(sales_df["sale_id"])]


print("Cleaning E-Rickshaw Sales...")
er_df = pd.read_csv(os.path.join(RAW_DIR, "erickshaw_sales.csv"))
er_df["enquiry_date"] = pd.to_datetime(er_df["enquiry_date"])
er_df["booking_date"] = pd.to_datetime(er_df["booking_date"])
er_df["delivery_date"] = pd.to_datetime(er_df["delivery_date"])

# Date Sequence Validation: delivery_date >= booking_date >= enquiry_date
# Fill missing or impossible enquiry dates with booking_date
er_df["enquiry_date"] = np.where(
    er_df["enquiry_date"].isna() | (er_df["enquiry_date"] > er_df["booking_date"]), 
    er_df["booking_date"], 
    er_df["enquiry_date"]
)
er_df["delivery_date"] = np.where(
    er_df["delivery_date"] < er_df["booking_date"], 
    er_df["booking_date"] + pd.Timedelta(days=3), 
    er_df["delivery_date"]
)


print("Cleaning Purchases & Purchase Orders...")
purch_df = pd.read_csv(os.path.join(RAW_DIR, "purchases.csv"))
po_df = pd.read_csv(os.path.join(RAW_DIR, "purchase_orders.csv"))
report_stats["purchase_orders"]["before_rows"] = len(po_df)

purch_df["purchase_date"] = pd.to_datetime(purch_df["purchase_date"])
po_df["po_date"] = pd.to_datetime(po_df["po_date"])
po_df["expected_delivery_date"] = pd.to_datetime(po_df["expected_delivery_date"])
po_df["actual_delivery_date"] = pd.to_datetime(po_df["actual_delivery_date"])

# Date sequence check: actual_delivery_date >= po_date
po_df["actual_delivery_date"] = np.where(
    po_df["actual_delivery_date"] < po_df["po_date"],
    po_df["expected_delivery_date"],
    po_df["actual_delivery_date"]
)

# Delivery Delay: actual_delivery_date - expected_delivery_date
po_df["delivery_delay_days"] = (po_df["actual_delivery_date"] - po_df["expected_delivery_date"]).dt.days
# For orders not yet delivered, delay is NULL
po_df["delivery_delay_days"] = np.where(po_df["actual_delivery_date"].isna(), None, po_df["delivery_delay_days"])

report_stats["purchase_orders"]["shortfalls"] = (po_df["quantity_received"] < po_df["quantity_ordered"]).sum()
report_stats["purchase_orders"]["after_rows"] = len(po_df)


print("Cleaning Expenses, Promotions, Weather, Fuel Prices, Inflation...")
exp_df = pd.read_csv(os.path.join(RAW_DIR, "expenses.csv"))
promo_df = pd.read_csv(os.path.join(RAW_DIR, "promotions.csv"))
weather_df = pd.read_csv(os.path.join(RAW_DIR, "weather.csv"))
fuel_df = pd.read_csv(os.path.join(RAW_DIR, "fuel_prices.csv"))
infl_df = pd.read_csv(os.path.join(RAW_DIR, "inflation.csv"))
inv_df = pd.read_csv(os.path.join(RAW_DIR, "inventory.csv"))
fb_df = pd.read_csv(os.path.join(RAW_DIR, "customer_feedback.csv"))


# ── 3. High-Value Customer Feature Engineering ─────────────────

print("Engineering Customer RFM & CLV Features...")
# First, calculate Customer-level Metrics
# 1. Retail Sales Profit & Revenue
sales_with_items = sitems_df.merge(sales_df, on="sale_id", how="inner")
customer_retail = sales_with_items.groupby("customer_id").agg(
    retail_revenue=("unit_price", lambda x: sum(x * (1 - sales_with_items.loc[x.index, "discount_pct"]/100) * sales_with_items.loc[x.index, "quantity"])),
    retail_profit=("profit_amount", "sum"),
    retail_transactions=("sale_id", "nunique"),
    last_retail_date=("sale_date", "max")
).reset_index()

# 2. E-Rickshaw Profit & Revenue
er_df["profit_amount"] = er_df["amount"] - er_df["cost_price"]
customer_er = er_df.groupby("customer_id").agg(
    er_revenue=("amount", "sum"),
    er_profit=("profit_amount", "sum"),
    er_transactions=("er_sale_id", "count"),
    last_er_date=("booking_date", "max")
).reset_index()

# Combine Retail and E-Rickshaw metrics
customer_metrics = cust_df[["customer_id"]].merge(customer_retail, on="customer_id", how="left")
customer_metrics = customer_metrics.merge(customer_er, on="customer_id", how="left")

# Fill NaNs with 0
customer_metrics = customer_metrics.fillna(0)

# CLV (Sum of Retail and E-rickshaw profits)
customer_metrics["clv"] = customer_metrics["retail_profit"] + customer_metrics["er_profit"]

# Total Revenue (Sum of Retail and E-rickshaw revenues)
customer_metrics["total_revenue"] = customer_metrics["retail_revenue"] + customer_metrics["er_revenue"]

# Purchase Frequency (Sum of transactions)
customer_metrics["purchase_frequency"] = customer_metrics["retail_transactions"] + customer_metrics["er_transactions"]

# Average Basket Size (Total Retail Revenue / Total Retail Transactions)
customer_metrics["avg_basket_size"] = np.where(
    customer_metrics["retail_transactions"] > 0,
    customer_metrics["retail_revenue"] / customer_metrics["retail_transactions"],
    0.0
)

# Recency (Days since last transaction relative to MAX_DATE)
def get_recency(row):
    r_date = row["last_retail_date"]
    er_date = row["last_er_date"]
    dates = []
    if r_date != 0: dates.append(pd.to_datetime(r_date).date())
    if er_date != 0: dates.append(pd.to_datetime(er_date).date())
    
    if not dates:
        return 9999 # No purchases recorded
    
    last_active = max(dates)
    return (MAX_DATE - last_active).days

customer_metrics["recency"] = customer_metrics.apply(get_recency, axis=1)

# Repeat Customer Flag (Frequency > 1)
customer_metrics["repeat_customer_flag"] = np.where(customer_metrics["purchase_frequency"] > 1, 1, 0)

# First Purchase Date
first_retail = sales_df.groupby("customer_id")["sale_date"].min().reset_index().rename(columns={"sale_date": "first_retail"})
first_er = er_df.groupby("customer_id")["booking_date"].min().reset_index().rename(columns={"booking_date": "first_er"})
first_dates = cust_df[["customer_id"]].merge(first_retail, on="customer_id", how="left")
first_dates = first_dates.merge(first_er, on="customer_id", how="left")
def get_first_date(row):
    fr = row["first_retail"]
    fe = row["first_er"]
    dates = []
    if not pd.isna(fr): dates.append(pd.to_datetime(fr).date())
    if not pd.isna(fe): dates.append(pd.to_datetime(fe).date())
    if not dates:
        return None
    return min(dates)

cust_df["first_purchase_date"] = first_dates.apply(get_first_date, axis=1)

# RFM Scoring & Segmentation
# Recency Score (1-5, lower recency = higher score)
customer_metrics["R_score"] = pd.qcut(customer_metrics["recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')

# Frequency Score (1-5, higher frequency = higher score)
customer_metrics["F_score"] = pd.qcut(customer_metrics["purchase_frequency"], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Monetary Score (1-5, higher spend = higher score)
customer_metrics["M_score"] = pd.qcut(customer_metrics["total_revenue"], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert scores to numeric
customer_metrics["R_score"] = pd.to_numeric(customer_metrics["R_score"])
customer_metrics["F_score"] = pd.to_numeric(customer_metrics["F_score"])
customer_metrics["M_score"] = pd.to_numeric(customer_metrics["M_score"])

# Total RFM Score
customer_metrics["rfm_score"] = customer_metrics["R_score"] + customer_metrics["F_score"] + customer_metrics["M_score"]

# Segment Mapping Function
def segment_customer(rfm):
    if rfm >= 12:
        return "Champions"
    elif rfm >= 9:
        return "Loyal Customers"
    elif rfm >= 7:
        return "Promising"
    elif rfm >= 5:
        return "Need Attention"
    else:
        return "Lost"

customer_metrics["customer_segment"] = customer_metrics["rfm_score"].apply(segment_customer)

# Merge back into Customers Table
cust_df = cust_df.merge(
    customer_metrics[[
        "customer_id", "clv", "purchase_frequency", "recency", 
        "avg_basket_size", "customer_segment", "repeat_customer_flag"
    ]], 
    on="customer_id", 
    how="left"
)

# ── 4. Save Cleaned Data to CSVs ────────────────────────────────

print("Saving cleaned CSVs...")
cust_df.to_csv(os.path.join(CLEAN_DIR, "customers.csv"), index=False)
prod_df.to_csv(os.path.join(CLEAN_DIR, "products.csv"), index=False)
brand_df.to_csv(os.path.join(CLEAN_DIR, "brands.csv"), index=False)
cat_df.to_csv(os.path.join(CLEAN_DIR, "product_categories.csv"), index=False)
sup_df.to_csv(os.path.join(CLEAN_DIR, "suppliers.csv"), index=False)
wh_df.to_csv(os.path.join(CLEAN_DIR, "warehouses.csv"), index=False)
emp_df.to_csv(os.path.join(CLEAN_DIR, "employees.csv"), index=False)
promo_df.to_csv(os.path.join(CLEAN_DIR, "promotions.csv"), index=False)
inv_df.to_csv(os.path.join(CLEAN_DIR, "inventory.csv"), index=False)
purch_df.to_csv(os.path.join(CLEAN_DIR, "purchases.csv"), index=False)
po_df.to_csv(os.path.join(CLEAN_DIR, "purchase_orders.csv"), index=False)
sales_df.to_csv(os.path.join(CLEAN_DIR, "sales.csv"), index=False)
sitems_df.to_csv(os.path.join(CLEAN_DIR, "sales_items.csv"), index=False)
sret_df.to_csv(os.path.join(CLEAN_DIR, "sales_returns.csv"), index=False)
pay_df.to_csv(os.path.join(CLEAN_DIR, "payments.csv"), index=False)
exp_df.to_csv(os.path.join(CLEAN_DIR, "expenses.csv"), index=False)
er_df.drop(columns=["profit_amount"], errors="ignore").to_csv(os.path.join(CLEAN_DIR, "erickshaw_sales.csv"), index=False)
fb_df.to_csv(os.path.join(CLEAN_DIR, "customer_feedback.csv"), index=False)
weather_df.to_csv(os.path.join(CLEAN_DIR, "weather.csv"), index=False)
fuel_df.to_csv(os.path.join(CLEAN_DIR, "fuel_prices.csv"), index=False)
infl_df.to_csv(os.path.join(CLEAN_DIR, "inflation.csv"), index=False)

print("\nETL PIPELINE SUCCESSFULLY EXECUTED.")
print(f"Clean CSVs saved to: {CLEAN_DIR}")

# ── 5. Generate Cleaning Report ────────────────────────────────
print("Writing Cleaning Report...")
report_path = r"c:\Users\hawka\Swastik_Traders_project\Phase-3-ETL-Data-Cleaning\cleaning_report.md"
with open(report_path, "w", encoding="utf-8") as rf:
    rf.write("# Data Cleaning & ETL Execution Report\n\n")
    rf.write("## 1. Overview\n")
    rf.write("This report documents the metrics, validation outcomes, and details of the Phase 3 ETL pipeline.\n\n")
    
    rf.write("## 2. Table Cleaning Summary\n\n")
    rf.write("| Table | Before Rows | After Rows | Issues Handled | Detail |\n")
    rf.write("|---|---|---|---|---|\n")
    rf.write(f"| `customers` | {report_stats['customers']['before_rows']} | {report_stats['customers']['after_rows']} | {report_stats['customers']['missing_handled']} missing addresses, {report_stats['customers']['invalid_phones']} malformed phones | Imputed missing addresses to 'Not Provided'; validated phone formats and flagged invalid numbers |\n")
    rf.write(f"| `products` | {report_stats['products']['before_rows']} | {report_stats['products']['after_rows']} | {report_stats['products']['name_normalizations']} name inconsistencies | Standardized brand naming prefixes; categorized price buckets and estimated paint coverages |\n")
    rf.write(f"| `suppliers` | {report_stats['suppliers']['before_rows']} | {report_stats['suppliers']['after_rows']} | {report_stats['suppliers']['phone_normalizations']} masked numbers | Normalized 'XXXXXX' phone masks to '000000' |\n")
    rf.write(f"| `sales` | {report_stats['sales']['before_rows']} | {report_stats['sales']['after_rows']} | {report_stats['sales']['duplicates_removed']} double-billed items | Removed duplicate transactions based on customer, date, and amount |\n")
    rf.write(f"| `purchase_orders` | {report_stats['purchase_orders']['before_rows']} | {report_stats['purchase_orders']['after_rows']} | {report_stats['purchase_orders']['date_fixes']} delivery date anomalies | Adjusted delivery dates that occurred before purchase orders; calculated delay metrics and logged {report_stats['purchase_orders']['shortfalls']} order shortfalls |\n")
    
    rf.write("\n## 3. Feature Engineering Log\n\n")
    rf.write("The following domain-specific features were successfully calculated and appended to the dataset:\n\n")
    rf.write("- **Customer Lifetime Value (CLV)**: Cumulative gross profit across both paint and e-rickshaw sales per customer.\n")
    rf.write("- **RFM Segmentation**: Categorized customers into *Champions, Loyal Customers, Promising, Need Attention, Lost* segments using Recency, Frequency, and Monetary scoring.\n")
    rf.write("- **Seasonality & Context Flags**: Appended `festival_flag`, `holiday_flag`, `season` (`pre_monsoon`, `monsoon`, etc.), and `warehouse_expansion_flag` to sales.\n")
    rf.write("- **Price Bucketing**: Products binned into *Low, Medium, High* buckets using selling price quantiles.\n")
    rf.write("- **Paint Coverage Estimate**: Domain-specific estimation of coverage in sq ft per SKU based on pack size and paint type.\n")
    rf.write("- **Delivery Timeliness**: Calculated delay metrics (expected vs. actual delivery date) for all purchase orders.\n")
    rf.write("\nReport generated successfully on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

print("Report saved to:", report_path)
