"""
Swastik Traders — Synthetic Data Generator
Phase 1: Data Generation
Generates all 21 tables as CSV files to data/raw/

Run: python generate_data.py
Output: data/raw/*.csv
"""

import subprocess, sys

# Auto-install dependencies
for pkg in ["faker", "pandas", "numpy"]:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

import os
import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import date, timedelta, datetime

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(OUT, exist_ok=True)

START = date(2023, 4, 1)
END   = date(2026, 6, 30)
ALL_DATES = pd.date_range(START, END, freq="D")

# ─── Festival calendar ────────────────────────────────────────────────────────
FESTIVALS = {
    "Holi":             [date(2023,3,8),  date(2024,3,25), date(2025,3,14)],
    "Akshaya Tritiya":  [date(2023,4,22), date(2024,5,10), date(2025,4,30)],
    "Navratri":         [date(2023,10,15),date(2024,10,3), date(2025,9,22)],
    "Diwali":           [date(2023,11,12),date(2024,11,1), date(2025,10,20)],
    "Chhath Puja":      [date(2023,11,19),date(2024,11,7), date(2025,10,27)],
}

def festival_for_date(d: date):
    for name, dates in FESTIVALS.items():
        for fd in dates:
            if abs((d - fd).days) <= 7:
                return name
    return None

def seasonal_paint_multiplier(d: date):
    m = d.month
    if m in [3, 4, 5]:   return 1.35   # pre-monsoon exterior surge
    if m in [6, 7, 8, 9]: return 0.70  # monsoon dip
    if m in [10, 11]:    return 1.25   # post-monsoon + festival
    return 1.0

def festival_multiplier(d: date):
    name = festival_for_date(d)
    if name in ["Diwali", "Navratri"]:       return 1.8
    if name == "Akshaya Tritiya":            return 1.5
    if name in ["Holi", "Chhath Puja"]:      return 1.3
    return 1.0

print("=" * 55)
print("  Swastik Traders — Synthetic Data Generator")
print("=" * 55)


# ══════════════════════════════════════════════════════════
# STEP 1 — EXTERNAL REFERENCE TABLES
# ══════════════════════════════════════════════════════════

print("\n[1/3] Generating external reference tables...")

# ── 1a. weather ──────────────────────────────────────────
rows = []
for d in pd.date_range(date(2022, 7, 1), END, freq="D"):
    m = d.month
    season = (
        "pre_monsoon" if m in [3,4,5] else
        "monsoon"     if m in [6,7,8,9] else
        "winter"      if m in [11,12,1,2] else
        "post_monsoon"
    )
    rainfall = 0.0
    if season == "monsoon":
        rainfall = max(0, np.random.exponential(12))
    elif season == "pre_monsoon" and random.random() < 0.05:
        rainfall = max(0, np.random.exponential(5))

    temp_base = {
        "pre_monsoon": 38, "monsoon": 32, "post_monsoon": 28, "winter": 18
    }[season]
    temp = round(temp_base + np.random.normal(0, 3), 1)
    rows.append({
        "weather_id":    len(rows)+1,
        "date":          d.date(),
        "city":          "Ballia",
        "temperature_max": temp,
        "rainfall_mm":   round(rainfall, 2),
        "season":        season,
        "is_extreme":    1 if rainfall > 50 else 0,
    })
weather_df = pd.DataFrame(rows)
weather_df.to_csv(f"{OUT}/weather.csv", index=False)
print(f"  weather.csv          → {len(weather_df):,} rows")

# ── 1b. fuel_prices ──────────────────────────────────────
rows = []
petrol = 96.0
diesel = 89.0
for d in pd.date_range(date(2022, 7, 1), END, freq="D"):
    petrol = round(max(85, min(115, petrol + np.random.normal(0, 0.05))), 2)
    diesel = round(max(78, min(105, diesel + np.random.normal(0, 0.04))), 2)
    rows.append({
        "fuel_price_id": len(rows)+1,
        "date":          d.date(),
        "petrol_price":  petrol,
        "diesel_price":  diesel,
    })
fuel_df = pd.DataFrame(rows)
fuel_df.to_csv(f"{OUT}/fuel_prices.csv", index=False)
print(f"  fuel_prices.csv      → {len(fuel_df):,} rows")

# ── 1c. inflation ─────────────────────────────────────────
rows = []
cpi = 170.0
for y in range(2022, 2027):
    for m in range(1, 13):
        if date(y, m, 1) > END: break
        rate = round(np.random.uniform(4.5, 7.5), 2)
        cpi  = round(cpi * (1 + rate/1200), 3)
        rows.append({
            "inflation_id":       len(rows)+1,
            "month":              m,
            "year":               y,
            "cpi_index":          cpi,
            "inflation_rate_pct": rate,
        })
infl_df = pd.DataFrame(rows)
infl_df.to_csv(f"{OUT}/inflation.csv", index=False)
print(f"  inflation.csv        → {len(infl_df):,} rows")


# ══════════════════════════════════════════════════════════
# STEP 2 — DIMENSION TABLES
# ══════════════════════════════════════════════════════════

print("\n[2/3] Generating dimension tables...")

# ── 2a. product_categories ───────────────────────────────
cats = [
    (1, "Paint",           None,  "All paint products"),
    (2, "Interior Paint",  1,     "Interior wall emulsions, distemper, enamel"),
    (3, "Exterior Paint",  1,     "Exterior wall emulsions"),
    (4, "Primer",          1,     "Interior and exterior primers"),
    (5, "Putty",           1,     "Wall putty — white cement and acrylic"),
    (6, "Enamel & Distemper", 1,  "Enamel gloss and synthetic distemper"),
    (7, "Accessories",     None,  "Brushes, rollers, tape, thinner, tools"),
    (8, "Brush",           7,     "Paint brushes"),
    (9, "Roller",          7,     "Paint rollers and trays"),
    (10,"Other Accessory", 7,     "Tape, thinner, sandpaper, stirrer"),
    (11,"E-Rickshaw",      None,  "Electric rickshaw vehicles"),
]
cat_df = pd.DataFrame(cats, columns=["category_id","category_name","parent_category_id","description"])
cat_df.to_csv(f"{OUT}/product_categories.csv", index=False)
print(f"  product_categories.csv → {len(cat_df)} rows")

# ── 2b. brands ───────────────────────────────────────────
brands_data = [
    (1, "Asian Paints",  "paint",      "India", "Rajesh Sharma"),
    (2, "Indigo Paints", "paint",      "India", "Amit Verma"),
    (3, "JSW Paints",    "paint",      "India", "Priya Singh"),
    (4, "Saarthi",       "erickshaw",  "India", "Suresh Yadav"),
    (5, "City Life",     "erickshaw",  "India", "Manoj Gupta"),
]
brand_df = pd.DataFrame(brands_data, columns=["brand_id","brand_name","brand_type","country_of_origin","contact_person"])
brand_df.to_csv(f"{OUT}/brands.csv", index=False)
print(f"  brands.csv           → {len(brand_df)} rows")

# ── 2c. products ─────────────────────────────────────────
PAINT_PRODUCTS = [
    # (brand_id, name, category_id, colors, sizes_L_or_kg, base_cost, base_sell)
    # Interior
    (1,"Tractor Emulsion",         2,["White","Ivory","Cream"],   [1,4,10,20], 110, 140),
    (1,"Royale Shyne",             2,["White","Ivory","Cream"],   [1,4,10,20], 185, 240),
    (1,"Apcolite Premium Emulsion",2,["White","Ivory","Cream"],   [1,4,10,20], 145, 185),
    (2,"Infinity Interior Emulsion",2,["White","Ivory","Cream"],  [1,4,10,20], 120, 155),
    (2,"Plasto Emulsion Plus",     2,["White","Ivory","Cream"],   [1,4,10,20], 105, 135),
    (3,"Joie Interior Emulsion",   2,["White","Ivory","Cream"],   [1,4,10,20], 100, 130),
    # Exterior
    (1,"Apex Exterior",            3,["White","Ivory","Cream"],   [1,4,10,20], 160, 205),
    (1,"Apex Ultima",              3,["White","Ivory","Cream"],   [1,4,10,20], 215, 275),
    (1,"Ace Exterior",             3,["White","Ivory","Cream"],   [4,10,20],   130, 165),
    (2,"Elastomeric Exterior Emulsion",3,["White","Ivory","Cream"],[4,10,20],  170, 218),
    (2,"All Season Exterior Emulsion",3,["White","Ivory","Cream"],[4,10,20],   150, 192),
    (3,"Joie Exterior Emulsion",   3,["White","Ivory","Cream"],   [4,10,20],   125, 158),
    # Enamel & Distemper
    (1,"Apcolite Enamel (Gloss)",  6,["White","Ivory","Cream"],   [0.5,1,4],   90,  118),
    (1,"Tractor Synthetic Distemper",6,["White","Ivory","Light Yellow"],[5,10,20],50,65),
    # Primer (white only)
    (1,"Wall Primer (WB)",         4,["White"],                   [4,10,20],   65,  82),
    (1,"Exterior Wall Primer",     4,["White"],                   [4,10,20],   72,  90),
    (2,"Exterior Wall Primer",     4,["White"],                   [4,10,20],   68,  85),
    (2,"Water Thinnable Cement Primer",4,["White"],               [4,10,20],   60,  75),
    (3,"Joie Primer (Interior)",   4,["White"],                   [4,10],      58,  72),
    (3,"Joie Primer (Exterior)",   4,["White"],                   [4,10],      62,  77),
    # Putty (white only — LOWEST MARGIN)
    (1,"TruCare Wall Care Putty",  5,["White"],                   [5,10,20,40],28,  30),
    (2,"Polymer Putty",            5,["White"],                   [10,20,40],  30,  32),
    (2,"Acrylic Wall Putty",       5,["White"],                   [1,10,20],   32,  34),
    (3,"Acrylic Wall Putty",       5,["White"],                   [10,20],     29,  31),
    (3,"Cement Putty",             5,["White"],                   [10,20],     27,  29),
]

ACCESSORY_PRODUCTS = [
    # (name, cat_id, sizes, unit, cost, sell)
    ("Paint Brush 1 inch",  8, None, "piece", 12,  18),
    ("Paint Brush 2 inch",  8, None, "piece", 18,  28),
    ("Paint Brush 3 inch",  8, None, "piece", 25,  38),
    ("Paint Brush 4 inch",  8, None, "piece", 35,  52),
    ("Paint Roller 4 inch", 9, None, "piece", 55,  85),
    ("Paint Roller 6 inch", 9, None, "piece", 75, 115),
    ("Paint Roller 9 inch", 9, None, "piece", 95, 145),
    ("Roller Tray",         9, None, "piece", 40,  62),
    ("Masking Tape 1 inch",10, None, "piece", 18,  28),
    ("Masking Tape 2 inch",10, None, "piece", 28,  42),
    ("Turpentine 500ml",   10, None, "piece", 35,  52),
    ("Turpentine 1L",      10, None, "piece", 62,  90),
    ("Putty Blade Small",  10, None, "piece", 15,  25),
    ("Putty Blade Medium", 10, None, "piece", 22,  35),
    ("Putty Blade Large",  10, None, "piece", 30,  48),
    ("Sandpaper 60 grit",  10, None, "piece",  5,   8),
    ("Sandpaper 100 grit", 10, None, "piece",  5,   8),
    ("Sandpaper 180 grit", 10, None, "piece",  6,   9),
    ("Paint Stirrer",      10, None, "piece",  8,  12),
]

ER_PRODUCTS = [
    # (brand_id, name, cost, sell)
    (4,"Saarthi Standard (4-seater)", 95000, 108000),
    (4,"Saarthi Plus (5-seater)",     108000,122000),
    (5,"City Life Mini (4-seater)",   88000, 100000),
]

products = []
pid = 1

# Paint products
COLOR_DEMAND = {"White": 1.0, "Ivory": 0.8, "Cream": 0.6, "Light Yellow": 0.3}

for brand_id, name, cat_id, colors, sizes, base_cost, base_sell in PAINT_PRODUCTS:
    unit = "kg" if cat_id == 5 else "litre"  # putty in kg
    for color in colors:
        for size in sizes:
            cost  = round(base_cost * size * (1 + np.random.uniform(-0.03, 0.03)), 2)
            sell  = round(base_sell * size * (1 + np.random.uniform(-0.02, 0.02)), 2)
            margin = round((sell - cost) / sell * 100, 2)
            products.append({
                "product_id":     pid,
                "product_name":   f"{['','Asian Paints','Indigo Paints','JSW Paints','Saarthi','City Life'][brand_id]} {name}",
                "category_id":    cat_id,
                "brand_id":       brand_id,
                "color":          color,
                "pack_size":      f"{size}{'kg' if unit=='kg' else 'L'}",
                "unit":           unit,
                "cost_price":     cost,
                "selling_price":  sell,
                "margin_pct":     margin,
                "min_stock_level":10,
                "is_active":      1,
            })
            pid += 1

# Accessory products (no color)
for name, cat_id, sizes, unit, cost, sell in ACCESSORY_PRODUCTS:
    margin = round((sell - cost) / sell * 100, 2)
    products.append({
        "product_id":     pid,
        "product_name":   name,
        "category_id":    cat_id,
        "brand_id":       1,  # Asian Paints branded
        "color":          None,
        "pack_size":      "1 piece",
        "unit":           unit,
        "cost_price":     float(cost),
        "selling_price":  float(sell),
        "margin_pct":     margin,
        "min_stock_level":20,
        "is_active":      1,
    })
    pid += 1

# E-Rickshaw products (no color column)
for brand_id, name, cost, sell in ER_PRODUCTS:
    margin = round((sell - cost) / sell * 100, 2)
    products.append({
        "product_id":     pid,
        "product_name":   name,
        "category_id":    11,
        "brand_id":       brand_id,
        "color":          None,
        "pack_size":      "1 unit",
        "unit":           "piece",
        "cost_price":     float(cost),
        "selling_price":  float(sell),
        "margin_pct":     margin,
        "min_stock_level":1,
        "is_active":      1,
    })
    pid += 1

# ── Inject ~5% naming inconsistencies ────────────────────
prod_df = pd.DataFrame(products)
inconsistency_indices = prod_df.sample(frac=0.05, random_state=7).index
for i in inconsistency_indices:
    name = prod_df.at[i, "product_name"]
    prod_df.at[i, "product_name"] = name.lower().replace("asian paints", "asian paints ltd").replace("indigo paints", "Indigo Paint")

prod_df.to_csv(f"{OUT}/products.csv", index=False)
print(f"  products.csv         → {len(prod_df):,} rows (SKUs)")

# ── 2d. suppliers ─────────────────────────────────────────
suppliers_data = [
    (1, "Asian Paints Distributor Ballia",    "paint_distributor",    "Ramesh Kumar",   "9415XXXXXX", "Ballia",     "immediate"),
    (2, "Asian Paints Distributor Gorakhpur", "paint_distributor",    "Sunil Tiwari",   "9839XXXXXX", "Gorakhpur",  "7_days"),
    (3, "Indigo Paints Distributor Varanasi", "paint_distributor",    "Vikram Singh",   "7007XXXXXX", "Varanasi",   "7_days"),
    (4, "Indigo Paints Distributor Patna",    "paint_distributor",    "Anil Mishra",    "9431XXXXXX", "Patna",      "15_days"),
    (5, "JSW Paints Distributor Lucknow",     "paint_distributor",    "Sanjay Pandey",  "9598XXXXXX", "Lucknow",    "15_days"),
    (6, "JSW Paints Distributor Varanasi",    "paint_distributor",    "Deepak Rai",     "9450XXXXXX", "Varanasi",   "7_days"),
    (7, "Saarthi E-Rickshaw OEM",             "erickshaw_oem",        "Mohit Srivastava","9935XXXXXX","Gorakhpur",  "immediate"),
    (8, "City Life E-Rickshaw OEM",           "erickshaw_oem",        "Rahul Yadav",    "9119XXXXXX", "Varanasi",   "immediate"),
    (9, "Ballia Hardware Wholesale",          "accessory_wholesaler", "Rajan Gupta",    "9838XXXXXX", "Ballia",     "immediate"),
    (10,"Purvanchal Accessories",             "accessory_wholesaler", "Ashok Verma",    "9792XXXXXX", "Ghazipur",   "7_days"),
    (11,"UP Paint Accessories Depot",         "accessory_wholesaler", "Prem Yadav",     "9415XXXXXX", "Varanasi",   "7_days"),
]
sup_df = pd.DataFrame(suppliers_data, columns=[
    "supplier_id","supplier_name","supplier_type","contact_person","phone","city","payment_terms"
])
sup_df["is_active"] = 1
sup_df.to_csv(f"{OUT}/suppliers.csv", index=False)
print(f"  suppliers.csv        → {len(sup_df)} rows")

# ── 2e. warehouses ────────────────────────────────────────
wh_data = [
    (1, "Godown 1", 800,  1, date(2022, 7, 1)),
    (2, "Godown 2", 1200, 1, date(2025, 2, 1)),  # operationalized 2025
]
wh_df = pd.DataFrame(wh_data, columns=[
    "warehouse_id","warehouse_name","capacity_sqft","is_active","operationalized_date"
])
wh_df.to_csv(f"{OUT}/warehouses.csv", index=False)
print(f"  warehouses.csv       → {len(wh_df)} rows")

# ── 2f. employees ─────────────────────────────────────────
emp_data = [
    (1, "Ramesh Agarwal",   "owner",      "9415100001", 0.00,     date(2022, 7, 1)),
    (2, "Suresh Agarwal",   "co_founder", "9415100002", 18000.00, date(2022, 7, 1)),
    (3, "Dinesh Gupta",     "co_founder", "9415100003", 18000.00, date(2022, 7, 1)),
    (4, "Ramu Yadav",       "labour",     "9839200001", 9000.00,  date(2022, 8, 1)),
    (5, "Shyam Patel",      "labour",     "9839200002", 9000.00,  date(2022, 9, 1)),
    (6, "Mohan Singh",      "labour",     "9839200003", 9500.00,  date(2023, 3, 1)),
    (7, "Lallan Yadav",     "labour",     "9839200004", 9500.00,  date(2024, 6, 1)),
]
emp_df = pd.DataFrame(emp_data, columns=[
    "employee_id","name","role","phone","monthly_salary","hire_date"
])
emp_df["is_active"] = 1
emp_df.to_csv(f"{OUT}/employees.csv", index=False)
print(f"  employees.csv        → {len(emp_df)} rows")

# ── 2g. promotions ────────────────────────────────────────
promo_rows = []
pid_p = 1
PROMO_EVENTS = [
    ("Holi Paint Offer",     "festival", date(2023,3,1),  date(2023,3,15), 8,  2),
    ("Summer Paint Sale",    "seasonal", date(2023,4,1),  date(2023,4,30), 5,  None),
    ("Diwali Paint Offer",   "festival", date(2023,10,25),date(2023,11,20),10, 2),
    ("Year End Clearance",   "discount", date(2023,12,15),date(2023,12,31),7,  None),
    ("Holi Paint Offer",     "festival", date(2024,3,15), date(2024,3,31), 8,  2),
    ("Akshaya Tritiya Deal", "festival", date(2024,5,3),  date(2024,5,17), 5,  None),
    ("Monsoon Dhamaka",      "seasonal", date(2024,7,1),  date(2024,7,31), 6,  None),
    ("Navratri Offer",       "festival", date(2024,9,25), date(2024,10,13),7,  2),
    ("Diwali Grand Sale",    "festival", date(2024,10,25),date(2024,11,10),12, 2),
    ("Winter Paint Discount","seasonal", date(2024,12,1), date(2024,12,31),6,  None),
    ("Holi Bonanza",         "festival", date(2025,3,5),  date(2025,3,20), 9,  2),
    ("Summer Savings",       "seasonal", date(2025,4,15), date(2025,5,15), 5,  None),
    ("Akshaya Tritiya Offer","festival", date(2025,4,22), date(2025,5,6),  6,  None),
    ("Navratri Festive Sale","festival", date(2025,9,14), date(2025,9,30), 8,  2),
    ("Diwali Mahotsav",      "festival", date(2025,10,12),date(2025,11,1), 12, 2),
    ("Chhath Special",       "festival", date(2025,10,28),date(2025,11,5), 6,  None),
    ("New Year Clearance",   "discount", date(2025,12,20),date(2025,12,31),8,  None),
    ("Summer Kick-off 2026", "seasonal", date(2026,4,1),  date(2026,5,31), 5,  None),
    ("Akshaya Tritiya 2026", "festival", date(2026,4,20), date(2026,5,4),  6,  None),
]
for name, ptype, sdate, edate, disc, min_amt_k in PROMO_EVENTS:
    promo_rows.append({
        "promotion_id":         pid_p,
        "promo_name":           name,
        "promo_type":           ptype,
        "start_date":           sdate,
        "end_date":             edate,
        "discount_pct":         disc,
        "applicable_category_id": None,
        "min_purchase_amount":  min_amt_k * 1000 if min_amt_k else None,
    })
    pid_p += 1
promo_df = pd.DataFrame(promo_rows)
promo_df.to_csv(f"{OUT}/promotions.csv", index=False)
print(f"  promotions.csv       → {len(promo_df)} rows")

# ── 2h. customers ─────────────────────────────────────────
AREAS = ["Mau Bazar","Sikta Mohalla","Rasra Road","Civil Lines","Kotwali",
         "Gai Ghat","Dubhar","Reoti","Bansdih","Sikandarpur"]
CUST_TYPES = ["retail","contractor","painter"]
CTYPE_WEIGHTS = [0.55, 0.25, 0.20]

customers = []
cid = 1
# Grow customer base over time — ~20/month avg
for d in pd.date_range(date(2022, 8, 1), END, freq="MS"):
    n_new = random.randint(12, 28)
    for _ in range(n_new):
        ctype = random.choices(CUST_TYPES, CTYPE_WEIGHTS)[0]
        phone = f"9{random.randint(100000000,999999999)}"
        # Dirty: 5% malformed phone
        if random.random() < 0.05:
            phone = phone[:random.randint(7,9)]  # truncate
        addr = fake.street_address() if random.random() > 0.08 else None  # 8% missing
        customers.append({
            "customer_id":          cid,
            "name":                 fake.name(),
            "phone":                phone,
            "address":              addr,
            "area":                 random.choice(AREAS),
            "customer_type":        ctype,
            "first_purchase_date":  None,  # filled during ETL from sales
        })
        cid += 1

cust_df = pd.DataFrame(customers)
cust_df.to_csv(f"{OUT}/customers.csv", index=False)
print(f"  customers.csv        → {len(cust_df):,} rows")


# ══════════════════════════════════════════════════════════
# STEP 3 — FACT TABLES
# ══════════════════════════════════════════════════════════

print("\n[3/3] Generating fact tables...")

# Helper lookups
paint_prods = prod_df[prod_df["category_id"].isin([2,3,4,5,6])]["product_id"].tolist()
putty_prods  = prod_df[prod_df["category_id"]==5]["product_id"].tolist()
acc_prods    = prod_df[prod_df["category_id"].isin([7,8,9,10])]["product_id"].tolist()
er_prods     = prod_df[prod_df["category_id"]==11]["product_id"].tolist()

prod_cost  = prod_df.set_index("product_id")["cost_price"].to_dict()
prod_sell  = prod_df.set_index("product_id")["selling_price"].to_dict()
prod_cat   = prod_df.set_index("product_id")["category_id"].to_dict()
prod_color = prod_df.set_index("product_id")["color"].to_dict()
prod_name  = prod_df.set_index("product_id")["product_name"].to_dict()
er_prod_names = {p: prod_name[p] for p in er_prods}

all_cust_ids = cust_df["customer_id"].tolist()
emp_ids_billing = [1, 2, 3]  # owner + co-founders handle billing
emp_ids_all     = emp_df["employee_id"].tolist()

def active_promo(d: date):
    for _, row in promo_df.iterrows():
        if pd.Timestamp(row["start_date"]).date() <= d <= pd.Timestamp(row["end_date"]).date():
            return row["promotion_id"], row["discount_pct"]
    return None, 0.0

def fuel_price_on(d: date):
    row = fuel_df[fuel_df["date"] == d]
    if len(row): return float(row.iloc[0]["petrol_price"])
    return 96.0

# ── 3a. inventory (initial snapshot) ──────────────────────
inv_rows = []
iid = 1
for _, p in prod_df.iterrows():
    for wh in [1, 2]:
        if wh == 2 and p["category_id"] == 11:
            continue  # e-rickshaws only in Godown 1
        base_qty = 50 if p["category_id"] == 5 else (  # putty — lots
                   30 if p["category_id"] in [2,3] else (
                   15 if p["category_id"] in [4,6] else (
                    5 if p["category_id"] in [7,8,9,10] else 2)))
        qty = max(0, int(base_qty * random.uniform(0.5, 1.8)))
        inv_rows.append({
            "inventory_id":      iid,
            "product_id":        p["product_id"],
            "warehouse_id":      wh,
            "quantity_in_stock": qty,
            "last_updated":      date(2023, 4, 1),
            "reorder_level":     max(3, int(base_qty * 0.2)),
            "dead_stock_flag":   0,
        })
        iid += 1
inv_df = pd.DataFrame(inv_rows)
inv_df.to_csv(f"{OUT}/inventory.csv", index=False)
print(f"  inventory.csv        → {len(inv_df):,} rows")

# ── 3b. purchases + 3c. purchase_orders ───────────────────
purch_rows = []
po_rows    = []
purch_id = 1
po_id    = 1

# ~2 procurement events per month, seasonal restock
months = pd.date_range(START, END, freq="MS")
for month_start in months:
    month_date = month_start.date()
    n_events = random.randint(1, 3)
    for _ in range(n_events):
        pdate = month_date + timedelta(days=random.randint(0, 27))
        sup_id = random.choice(sup_df["supplier_id"].tolist())
        sup_type = sup_df[sup_df["supplier_id"]==sup_id]["supplier_type"].values[0]

        # Select products based on supplier type
        if "paint" in sup_type:
            pool = paint_prods
        elif "erickshaw" in sup_type:
            pool = er_prods
        else:
            pool = acc_prods

        n_items = random.randint(3, 10)
        chosen  = random.choices(pool, k=min(n_items, len(pool)))
        total   = 0.0
        for prod_id in chosen:
            qty   = random.randint(5, 60) if prod_cat[prod_id] != 11 else random.randint(1, 3)
            uprice = prod_cost[prod_id] * random.uniform(0.97, 1.03)
            recv  = qty if random.random() > 0.08 else random.randint(int(qty*0.7), qty-1)
            exp_del = pdate + timedelta(days=random.randint(1, 5))
            delay   = random.choices([0, random.randint(1,5), random.randint(5,15)],
                                     weights=[0.70, 0.20, 0.10])[0]
            act_del = exp_del + timedelta(days=delay) if random.random() > 0.05 else None
            status  = "complete" if recv == qty else ("partial" if recv > 0 else "pending")
            po_rows.append({
                "po_id":                  po_id,
                "purchase_id":            purch_id,
                "product_id":             prod_id,
                "quantity_ordered":       qty,
                "quantity_received":      recv,
                "unit_price":             round(uprice, 2),
                "po_date":                pdate,
                "expected_delivery_date": exp_del,
                "actual_delivery_date":   act_del,
                "status":                 status,
            })
            total += uprice * qty
            po_id += 1

        wh_id = 1 if pdate < date(2025, 2, 1) else random.choice([1, 2])
        pay_status = random.choices(["paid","partial","pending"], weights=[0.75,0.15,0.10])[0]
        purch_rows.append({
            "purchase_id":    purch_id,
            "supplier_id":    sup_id,
            "warehouse_id":   wh_id,
            "purchase_date":  pdate,
            "total_amount":   round(total, 2),
            "payment_status": pay_status,
            "invoice_number": f"INV{purch_id:05d}",
        })
        purch_id += 1

purch_df = pd.DataFrame(purch_rows)
po_df    = pd.DataFrame(po_rows)
purch_df.to_csv(f"{OUT}/purchases.csv", index=False)
po_df.to_csv(f"{OUT}/purchase_orders.csv", index=False)
print(f"  purchases.csv        → {len(purch_df):,} rows")
print(f"  purchase_orders.csv  → {len(po_df):,} rows")

# ── 3d. sales + 3e. sales_items + 3f. payments ────────────
sale_rows  = []
sitem_rows = []
pay_rows   = []
sale_id  = 1
sitem_id = 1
pay_id   = 1

# Build daily sales volume
for d in pd.date_range(START, END, freq="D"):
    dd = d.date()
    base_n = random.randint(3, 8)
    mult   = seasonal_paint_multiplier(dd) * festival_multiplier(dd)
    n_sales = max(1, int(base_n * mult + np.random.normal(0, 0.8)))

    promo_id, disc_pct = active_promo(dd)

    for _ in range(n_sales):
        cust_id = random.choice(all_cust_ids)
        emp_id  = random.choice(emp_ids_billing)

        # Mix of items per sale
        n_items = random.choices([1,2,3,4,5], weights=[0.30,0.35,0.20,0.10,0.05])[0]

        # Item pool: weighted toward paint + putty, some accessories
        pool_weights = [0.55, 0.30, 0.15]
        pool_choice  = random.choices(["paint","putty","accessory"], pool_weights)[0]
        if pool_choice == "paint":
            chosen_pool = random.choices(
                [p for p in paint_prods if p not in putty_prods], k=n_items
            )
        elif pool_choice == "putty":
            chosen_pool = random.choices(putty_prods, k=n_items)
        else:
            chosen_pool = random.choices(acc_prods, k=n_items)

        total_amount = 0.0
        for pid_s in chosen_pool:
            qty_s  = random.randint(1, 15) if prod_cat[pid_s] in [5] else random.randint(1, 5)
            sell_p = prod_sell[pid_s]
            cost_p = prod_cost[pid_s]
            disc   = disc_pct / 100 if promo_id else 0.0
            net    = sell_p * (1 - disc)
            profit = round((net - cost_p) * qty_s, 2)
            wh_id  = 1 if dd < date(2025, 2, 1) else random.choice([1, 2])

            sitem_rows.append({
                "sale_item_id": sitem_id,
                "sale_id":      sale_id,
                "product_id":   pid_s,
                "warehouse_id": wh_id,
                "quantity":     qty_s,
                "unit_price":   round(sell_p, 2),
                "cost_price":   round(cost_p, 2),
                "discount_pct": round(disc_pct, 2) if promo_id else 0.0,
                "profit_amount":profit,
            })
            total_amount += net * qty_s
            sitem_id += 1

        total_amount = round(total_amount, 2)

        # Payment method: cash dominant for small, bank_transfer for large
        if total_amount > 5000:
            pmeth = random.choices(["cash","upi","bank_transfer"], [0.30,0.35,0.35])[0]
        else:
            pmeth = random.choices(["cash","upi","bank_transfer"], [0.60,0.35,0.05])[0]

        pay_status_sale  = random.choices(["paid","pending"], [0.92, 0.08])[0]
        pay_date = dd if pay_status_sale == "paid" else dd + timedelta(days=random.randint(1,3))
        t_ref = f"UPI{pay_id:08d}" if pmeth == "upi" else (f"BT{pay_id:08d}" if pmeth == "bank_transfer" else None)

        # Dirty: 2% duplicate-like entries (same cust, same day, same amount)
        if random.random() < 0.02:
            dd_dirty = dd  # same date
        else:
            dd_dirty = dd

        sale_rows.append({
            "sale_id":        sale_id,
            "customer_id":    cust_id,
            "employee_id":    emp_id,
            "sale_date":      dd_dirty,
            "total_amount":   total_amount,
            "payment_method": pmeth,
            "payment_status": pay_status_sale,
            "promotion_id":   promo_id,
        })
        pay_rows.append({
            "payment_id":       pay_id,
            "sale_id":          sale_id,
            "payment_method":   pmeth,
            "payment_date":     pay_date,
            "amount":           total_amount,
            "payment_status":   "completed" if pay_status_sale == "paid" else "pending",
            "transaction_ref":  t_ref,
        })
        sale_id  += 1
        pay_id   += 1

sale_df  = pd.DataFrame(sale_rows)
sitem_df = pd.DataFrame(sitem_rows)
pay_df   = pd.DataFrame(pay_rows)
sale_df.to_csv(f"{OUT}/sales.csv", index=False)
sitem_df.to_csv(f"{OUT}/sales_items.csv", index=False)
pay_df.to_csv(f"{OUT}/payments.csv", index=False)
print(f"  sales.csv            → {len(sale_df):,} rows")
print(f"  sales_items.csv      → {len(sitem_df):,} rows")
print(f"  payments.csv         → {len(pay_df):,} rows")

# ── 3g. sales_returns ─────────────────────────────────────
ret_rows = []
rid = 1
# Sample ~1.5% of paint sales for returns
return_candidates = sale_df.sample(frac=0.015, random_state=99)
REASONS = ["Wrong colour ordered","Damaged packaging","Customer changed mind",
           "Quality issue","Excess quantity ordered"]
for _, sr in return_candidates.iterrows():
    sid = int(sr["sale_id"])
    sitems_for_sale = sitem_df[sitem_df["sale_id"]==sid]
    if sitems_for_sale.empty: continue
    item = sitems_for_sale.sample(1).iloc[0]
    qty_ret = random.randint(1, int(item["quantity"]))
    refund  = round(qty_ret * item["unit_price"] * (1 - item["discount_pct"]/100), 2)
    ret_rows.append({
        "return_id":        rid,
        "sale_id":          sid,
        "product_id":       item["product_id"],
        "return_date":      pd.Timestamp(sr["sale_date"]).date() + timedelta(days=random.randint(1,7)),
        "quantity_returned":qty_ret,
        "reason":           random.choice(REASONS),
        "refund_amount":    refund,
        "status":           random.choice(["processed","processed","pending"]),
    })
    rid += 1
ret_df = pd.DataFrame(ret_rows)
ret_df.to_csv(f"{OUT}/sales_returns.csv", index=False)
print(f"  sales_returns.csv    → {len(ret_df):,} rows")

# ── 3h. erickshaw_sales ───────────────────────────────────
er_rows = []
erid = 1
for d in pd.date_range(START, END, freq="D"):
    dd = d.date()
    fest = festival_for_date(dd)
    # Base probability ~1/12 per day (≈1 per 2 weeks)
    # Spike on Akshaya Tritiya, Diwali, Navratri
    if fest == "Akshaya Tritiya":
        prob = 0.4
    elif fest in ["Diwali","Navratri","Chhath Puja"]:
        prob = 0.35
    elif fest == "Holi":
        prob = 0.15
    else:
        prob = 0.075

    # Fuel price effect: higher fuel → higher probability (2-week lag approx)
    fp = fuel_price_on(dd - timedelta(days=14))
    fuel_boost = max(0, (fp - 96) / 96 * 0.5)
    prob = min(0.95, prob + fuel_boost)

    if random.random() < prob:
        er_prod_id = random.choice(er_prods)
        cust_id    = random.choice(all_cust_ids)
        emp_id     = random.choice([1, 2, 3])
        book_date  = dd
        del_date   = dd + timedelta(days=random.randint(1, 7))
        pay_meth   = random.choices(["bank_transfer","upi","cash"], [0.60, 0.30, 0.10])[0]
        pay_stat   = random.choices(["paid","partial","pending"], [0.70, 0.20, 0.10])[0]
        amount     = prod_sell[er_prod_id]
        cost       = prod_cost[er_prod_id]

        er_rows.append({
            "er_sale_id":      erid,
            "customer_id":     cust_id,
            "employee_id":     emp_id,
            "product_id":      er_prod_id,
            "enquiry_date":    dd - timedelta(days=random.randint(0, 5)),
            "booking_date":    book_date,
            "delivery_date":   del_date,
            "amount":          float(amount),
            "cost_price":      float(cost),
            "payment_method":  pay_meth,
            "payment_status":  pay_stat,
            "er_model":        prod_name[er_prod_id],
            "festive_occasion": fest,
        })
        erid += 1

er_df = pd.DataFrame(er_rows)
er_df.to_csv(f"{OUT}/erickshaw_sales.csv", index=False)
print(f"  erickshaw_sales.csv  → {len(er_df):,} rows")

# ── 3i. expenses ──────────────────────────────────────────
exp_rows = []
eid = 1
for month_start in pd.date_range(date(2022, 7, 1), END, freq="MS"):
    m = month_start.date()
    # Salary — monthly
    salary_total = sum(emp_df[emp_df["hire_date"] <= m]["monthly_salary"])
    exp_rows.append({
        "expense_id":   eid, "expense_date": m,
        "category":     "salary", "amount": round(salary_total, 2),
        "approved_by":  1, "description": f"Monthly salary {m.strftime('%b %Y')}",
    }); eid += 1
    # Utilities
    util = round(random.uniform(2500, 5000), 2)
    exp_rows.append({
        "expense_id":   eid, "expense_date": m,
        "category":     "utilities", "amount": util,
        "approved_by":  1, "description": "Electricity + water",
    }); eid += 1
    # Maintenance (quarterly-ish)
    if random.random() < 0.25:
        maint = round(random.uniform(1000, 8000), 2)
        exp_rows.append({
            "expense_id":   eid, "expense_date": m + timedelta(days=random.randint(0,20)),
            "category":     "maintenance", "amount": maint,
            "approved_by":  1, "description": "Godown/shop maintenance",
        }); eid += 1
    # Marketing (rare — organic mostly)
    if random.random() < 0.15:
        mkt = round(random.uniform(500, 3000), 2)
        exp_rows.append({
            "expense_id":   eid, "expense_date": m + timedelta(days=random.randint(0,20)),
            "category":     "marketing", "amount": mkt,
            "approved_by":  1, "description": "Local pamphlets / newspaper ad",
        }); eid += 1

# One-time setup cost in July 2022
exp_rows.append({
    "expense_id":   eid, "expense_date": date(2022, 7, 5),
    "category":     "one_time_setup", "amount": 1000000.00,
    "approved_by":  1, "description": "Shop fit-out, godown racks, signage, initial setup ~10L",
}); eid += 1

exp_df = pd.DataFrame(exp_rows)
exp_df.to_csv(f"{OUT}/expenses.csv", index=False)
print(f"  expenses.csv         → {len(exp_df):,} rows")

# ── 3j. customer_feedback ─────────────────────────────────
fb_rows = []
fid = 1
SOURCES   = ["in_store","whatsapp","google_maps"]
S_WEIGHTS = [0.50, 0.35, 0.15]
FB_CATS   = ["product_quality","service","price","availability"]

# ~20% of sales trigger feedback
for _, s in sale_df.sample(frac=0.20, random_state=5).iterrows():
    rating = random.choices([1,2,3,4,5], weights=[0.03,0.07,0.15,0.45,0.30])[0]
    sent   = "positive" if rating >= 4 else ("neutral" if rating == 3 else "negative")
    review_texts = {
        5: ["Bahut acha service mila", "Best paint shop in Ballia", "Good quality products, will come again"],
        4: ["Nice shop, helpful staff", "Good range of paints", "Satisfied with purchase"],
        3: ["Average service", "Product ok, price thoda zyada", "Could be better"],
        2: ["Delivery late", "Staff not helpful", "Quality not as expected"],
        1: ["Very bad experience", "Wrong product delivered", "Not recommended"],
    }
    fb_rows.append({
        "feedback_id":       fid,
        "customer_id":       int(s["customer_id"]),
        "sale_id":           int(s["sale_id"]),
        "feedback_date":     pd.Timestamp(s["sale_date"]).date() + timedelta(days=random.randint(0,3)),
        "source":            random.choices(SOURCES, S_WEIGHTS)[0],
        "rating":            rating,
        "review_text":       random.choice(review_texts[rating]),
        "sentiment":         None,  # filled by Phase 6 NLP
        "feedback_category": random.choice(FB_CATS),
    })
    fid += 1
fb_df = pd.DataFrame(fb_rows)
fb_df.to_csv(f"{OUT}/customer_feedback.csv", index=False)
print(f"  customer_feedback.csv → {len(fb_df):,} rows")


# ══════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════

print("\n" + "=" * 55)
print("  ✅  Data Generation Complete")
print("=" * 55)

all_csvs = [
    ("weather.csv",            len(weather_df)),
    ("fuel_prices.csv",        len(fuel_df)),
    ("inflation.csv",          len(infl_df)),
    ("product_categories.csv", len(cat_df)),
    ("brands.csv",             len(brand_df)),
    ("products.csv",           len(prod_df)),
    ("suppliers.csv",          len(sup_df)),
    ("warehouses.csv",         len(wh_df)),
    ("employees.csv",          len(emp_df)),
    ("promotions.csv",         len(promo_df)),
    ("customers.csv",          len(cust_df)),
    ("inventory.csv",          len(inv_df)),
    ("purchases.csv",          len(purch_df)),
    ("purchase_orders.csv",    len(po_df)),
    ("sales.csv",              len(sale_df)),
    ("sales_items.csv",        len(sitem_df)),
    ("payments.csv",           len(pay_df)),
    ("sales_returns.csv",      len(ret_df)),
    ("erickshaw_sales.csv",    len(er_df)),
    ("expenses.csv",           len(exp_df)),
    ("customer_feedback.csv",  len(fb_df)),
]
total_rows = sum(r for _, r in all_csvs)
print(f"\n  {'Table':<30} {'Rows':>8}")
print(f"  {'-'*38}")
for name, rows in all_csvs:
    print(f"  {name:<30} {rows:>8,}")
print(f"  {'-'*38}")
print(f"  {'TOTAL':<30} {total_rows:>8,}")
print(f"\n  Output: {OUT}")
