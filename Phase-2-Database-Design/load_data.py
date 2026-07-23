import os
import getpass
import pymysql
import pandas as pd
import numpy as np

# Connection parameters
DB_HOST = "localhost"
DB_USER = "root"
DB_NAME = "swastik_traders"
RAW_DATA_DIR = r"c:\Users\hawka\Swastik_Traders_project\Phase-1-Data-Generation\data\raw"

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

def load_table(conn, table_name, csv_name):
    csv_path = os.path.join(RAW_DATA_DIR, csv_name)
    if not os.path.exists(csv_path):
        print(f"  WARNING: File not found: {csv_path}. Skipping.")
        return

    # Read CSV, replacing empty strings and other NA symbols with None (SQL NULL)
    df = pd.read_csv(csv_path)
    df = df.replace({np.nan: None})

    columns = list(df.columns)
    col_placeholders = ", ".join(["%s"] * len(columns))
    col_names = ", ".join(columns)
    
    query = f"INSERT INTO {table_name} ({col_names}) VALUES ({col_placeholders})"
    
    # Convert dataframe rows to list of tuples
    data_tuples = [tuple(row) for row in df.itertuples(index=False, name=None)]
    
    with conn.cursor() as cursor:
        cursor.executemany(query, data_tuples)
    
    conn.commit()
    print(f"  Successfully loaded {len(df):,} rows into {table_name}")

def main():
    print("=" * 60)
    print("  Swastik Traders — Bulk Data Loader")
    print("=" * 60)
    
    # Prompt for database password
    db_password = getpass.getpass("Enter MySQL password for 'root' (leave empty if none): ")
    
    try:
        # Test connection first without specifying DB to ensure we can connect
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=db_password,
            charset="utf8mb4",
            autocommit=False
        )
        print("Connected to MySQL server.")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    try:
        with conn.cursor() as cursor:
            # Ensure DB exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE {DB_NAME};")
        conn.select_db(DB_NAME)
        
        # Disable FK checks during load
        print("Disabling foreign key checks...")
        with conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
        # Load tables
        for table_name, csv_name in tables:
            print(f"Loading {table_name}...")
            try:
                load_table(conn, table_name, csv_name)
            except Exception as load_err:
                print(f"  ERROR loading {table_name}: {load_err}")
                
        # Re-enable FK checks
        print("Re-enabling foreign key checks...")
        with conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        
        print("\nSUCCESS: All data loaded successfully.")
    except Exception as e:
        print(f"\nAn error occurred during data load: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Connection closed.")
        print("=" * 60)

if __name__ == "__main__":
    main()
