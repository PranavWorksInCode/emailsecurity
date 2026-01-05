import sqlite3
import pandas as pd
import os

db_path = "audit_log.db"

if not os.path.exists(db_path):
    print(f"ERROR: {db_path} does not exist.")
else:
    print(f"Checking database at: {os.path.abspath(db_path)}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {tables}")
        
        if tables:
            # Check row count
            df = pd.read_sql_query("SELECT * FROM scan_logs", conn)
            print(f"Total Rows: {len(df)}")
            if not df.empty:
                print("Last 5 rows:")
                print(df.tail())
            else:
                print("Table 'scan_logs' is empty.")
        else:
            print("No tables found! DB is initialized but empty.")
            
    except Exception as e:
        print(f"Database Error: {e}")
