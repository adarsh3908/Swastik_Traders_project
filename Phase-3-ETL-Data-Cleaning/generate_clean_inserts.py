import os
import pandas as pd
import numpy as np

# Paths
CLEAN_DATA_DIR = r"c:\Users\hawka\Swastik_Traders_project\Phase-3-ETL-Data-Cleaning\cleaned_csv"
OUTPUT_SQL = r"c:\Users\hawka\Swastik_Traders_project\Phase-3-ETL-Data-Cleaning\clean_insert_data.sql"

# List of tables and CSV names in order of FK dependencies
tables = [
    ("product_categories", "product_categories.csv"),
    ("brands", "brands.csv"),
    ("suppliers", "suppliers.csv"),
    ("warehouses", "warehouses.csv"),
    ("employees", "employees.csv"),
    ("promotions", "promotions.csv"),
    ("customers", "customers.csv"),
    ("products", "products.csv"),
    ("weather", "weather.csv"),
    ("fuel_prices", "fuel_prices.csv"),
    ("inflation", "inflation.csv"),
    ("inventory", "inventory.csv"),
    ("purchases", "purchases.csv"),
    ("purchase_orders", "purchase_orders.csv"),
    ("sales", "sales.csv"),
    ("payments", "payments.csv"),
    ("expenses", "expenses.csv"),
    ("erickshaw_sales", "erickshaw_sales.csv"),
    ("customer_feedback", "customer_feedback.csv"),
    ("sales_items", "sales_items.csv"),
    ("sales_returns", "sales_returns.csv")
]

# Set of numeric columns for each table to avoid quoting them in SQL (including new engineered fields)
numeric_columns = {
    "product_categories": {"category_id", "parent_category_id"},
    "brands": {"brand_id"},
    "suppliers": {"supplier_id", "is_active"},
    "warehouses": {"warehouse_id", "capacity_sqft", "is_active"},
    "employees": {"employee_id", "monthly_salary", "is_active"},
    "promotions": {"promotion_id", "discount_pct", "applicable_category_id", "min_purchase_amount"},
    "customers": {
        "customer_id", "clv", "purchase_frequency", "recency", 
        "avg_basket_size", "repeat_customer_flag", "is_valid_phone"
    },
    "products": {
        "product_id", "category_id", "brand_id", "cost_price", "selling_price", 
        "margin_pct", "min_stock_level", "is_active", "paint_coverage_sqft_estimate"
    },
    "weather": {"weather_id", "temperature_max", "rainfall_mm", "is_extreme"},
    "fuel_prices": {"fuel_price_id", "petrol_price", "diesel_price"},
    "inflation": {"inflation_id", "month", "year", "cpi_index", "inflation_rate_pct"},
    "inventory": {"inventory_id", "product_id", "warehouse_id", "quantity_in_stock", "reorder_level", "dead_stock_flag"},
    "purchases": {"purchase_id", "supplier_id", "warehouse_id", "total_amount"},
    "purchase_orders": {"po_id", "purchase_id", "product_id", "quantity_ordered", "quantity_received", "unit_price", "delivery_delay_days"},
    "sales": {"sale_id", "customer_id", "employee_id", "total_amount", "promotion_id", "festival_flag", "holiday_flag", "warehouse_expansion_flag"},
    "payments": {"payment_id", "sale_id", "amount"},
    "expenses": {"expense_id", "amount", "approved_by"},
    "erickshaw_sales": {"er_sale_id", "customer_id", "employee_id", "product_id", "amount", "cost_price"},
    "customer_feedback": {"feedback_id", "customer_id", "sale_id", "rating"},
    "sales_items": {"sale_item_id", "sale_id", "product_id", "warehouse_id", "quantity", "unit_price", "cost_price", "discount_pct", "profit_amount"},
    "sales_returns": {"return_id", "sale_id", "product_id", "quantity_returned", "refund_amount"}
}

def clean_value(val, col_name, table_name):
    if pd.isna(val) or val is None or str(val).strip().lower() in ['nan', 'null', '<na>', '']:
        return "NULL"
    
    val_str = str(val).strip()
    
    if col_name in numeric_columns.get(table_name, set()):
        try:
            f_val = float(val_str)
            if f_val.is_integer():
                return str(int(f_val))
            return f"{f_val:.4f}".rstrip('0').rstrip('.')
        except ValueError:
            return "NULL"
            
    escaped_str = val_str.replace("'", "''")
    return f"'{escaped_str}'"

def main():
    print("=" * 60)
    print("  Swastik Traders — Clean SQL Insert Script Generator")
    print("=" * 60)
    
    with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
        f.write("-- ============================================================\n")
        f.write("-- Swastik Traders — Cleaned & Enriched Seed Data Inserts\n")
        f.write("-- Automatically generated from Phase 3 Cleaned CSV files\n")
        f.write("-- ============================================================\n\n")
        f.write("USE swastik_traders_clean;\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        
        for table_name, csv_name in tables:
            csv_path = os.path.join(CLEAN_DATA_DIR, csv_name)
            if not os.path.exists(csv_path):
                print(f"ERROR: File not found: {csv_path}")
                continue
                
            print(f"Processing {csv_name}...")
            f.write(f"-- ── Seed Table: {table_name} ─────────────────────────────\n")
            
            df = pd.read_csv(csv_path, dtype=str)
            columns_str = ", ".join(df.columns)
            
            batch_size = 1000
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i : i + batch_size]
                values_list = []
                for _, row in batch_df.iterrows():
                    formatted_vals = [clean_value(row[col], col, table_name) for col in df.columns]
                    values_list.append("(" + ", ".join(formatted_vals) + ")")
                
                f.write(f"INSERT INTO {table_name} ({columns_str}) VALUES\n")
                f.write(",\n".join(values_list) + ";\n\n")
                
            print(f"  Successfully wrote {len(df):,} rows for {table_name}")
            
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        
    print("\nSUCCESS: clean_insert_data.sql has been successfully generated at:")
    print(OUTPUT_SQL)
    print("=" * 60)

if __name__ == "__main__":
    main()
