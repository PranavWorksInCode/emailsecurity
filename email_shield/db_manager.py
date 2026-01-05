import sqlite3
import datetime
import os

DB_NAME = "audit_log.db"

class DBManager:
    def __init__(self):
        self.conn = None
        self.init_db()

    def init_db(self):
        """Creates the table if it doesn't exist."""
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                filename TEXT,
                user_email TEXT,
                verdict TEXT,
                url_detected TEXT
            )
        ''')
        self.conn.commit()

    def log_scan(self, filename, user_email, verdict, url_detected="N/A"):
        """Inserts a new scan record."""
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO scan_logs (timestamp, filename, user_email, verdict, url_detected)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, filename, user_email, verdict, url_detected))
        self.conn.commit()

    def get_all_logs(self):
        """Fetches all logs for the dashboard."""
        import pandas as pd
        return pd.read_sql_query("SELECT * FROM scan_logs", self.conn)
