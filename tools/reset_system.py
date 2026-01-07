import os
import shutil
import sqlite3

# Config matches project structure
DB_PATH = "audit_log.db"
DIRS_TO_CLEAR = [
    "email_shield/incoming",
    "email_shield/inbox",
    "email_shield/quarantine"
]

def reset_system():
    print("--- System Reset Initiated ---")
    
    # 1. Clear Database
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[OK] Deleted database: {DB_PATH}")
        except PermissionError:
            print(f"[!] Database file is locked (likely by Dashboard). Attempting SQL delete...")
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                # Check if table exists
                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_logs'")
                if c.fetchone():
                    c.execute("DELETE FROM scan_logs")
                    c.execute("DELETE FROM sqlite_sequence WHERE name='scan_logs'") # Reset Auto-ID
                    conn.commit()
                    c.execute("VACUUM") # Reclaim space
                    print(f"[OK] Cleared all records from 'scan_logs' table.")
                    
                    # Also drop sender_email column? No, we want to keep the schema.
                    # Actually, if we want to "Start from 0", emptying the table is perfect.
                    # But if the schema was "old", we might want to update it.
                    # Since we updated db_manager to migrate, this is fine.
                else:
                    print("[!] Table 'scan_logs' not found.")
                conn.close()
            except Exception as e_sql:
                print(f"[X] Failed to clear DB via SQL: {e_sql}")

        except Exception as e:
            print(f"[X] Failed to delete DB: {e}")
    else:
        print(f"[!] Database not found: {DB_PATH}")

    # 2. Clear Directories
    for d in DIRS_TO_CLEAR:
        if os.path.exists(d):
            # Delete all files in directory
            for filename in os.listdir(d):
                file_path = os.path.join(d, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"[X] Failed to delete {file_path}. Reason: {e}")
            print(f"[OK] Cleared directory: {d}")
        else:
            print(f"[!] Directory not found: {d}")

    print("\nSystem cleared. You are ready to start fresh.")

if __name__ == "__main__":
    reset_system()
