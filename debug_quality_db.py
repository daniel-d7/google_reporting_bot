#!/usr/bin/env python3
"""
Debug script for quality check SQLite database
Shows the content of the quality_check.db file
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime

def debug_quality_db():
    """Debug the quality check database"""
    db_path = os.path.join(os.path.dirname(__file__), 'quality_check.db')
    
    print(f"🔍 Debugging quality check database...")
    print(f"Database path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist yet. Run the quality check first.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Check if table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            if ('quality_checks',) not in tables:
                print("❌ quality_checks table does not exist yet.")
                return
            
            # Show all records
            print("\n📋 All quality check records:")
            df = pd.read_sql_query("SELECT * FROM quality_checks ORDER BY timestamp", conn)
            if df.empty:
                print("   No records found.")
            else:
                print(df.to_string(index=False))
            
            # Show current month records
            current_month = datetime.now().strftime('%Y-%m')
            print(f"\n📅 Records for current month ({current_month}):")
            df_month = pd.read_sql_query(
                "SELECT * FROM quality_checks WHERE month = ? ORDER BY timestamp", 
                conn, 
                params=(current_month,)
            )
            if df_month.empty:
                print("   No records found for current month.")
            else:
                print(df_month.to_string(index=False))
                
            # Show last record for current month
            print(f"\n🕒 Last record for current month:")
            cursor.execute("""
                SELECT * FROM quality_checks 
                WHERE month = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (current_month,))
            last_record = cursor.fetchone()
            if last_record:
                columns = [description[0] for description in cursor.description]
                record_dict = dict(zip(columns, last_record))
                for key, value in record_dict.items():
                    print(f"   {key}: {value}")
            else:
                print("   No records found for current month.")
                
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

def clear_quality_db():
    """Clear all records from the quality check database"""
    db_path = os.path.join(os.path.dirname(__file__), 'quality_check.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("DELETE FROM quality_checks")
            print("✅ All quality check records cleared.")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_quality_db()
    else:
        debug_quality_db()
        print("\nUsage:")
        print("  python debug_quality_db.py       - Show database contents")
        print("  python debug_quality_db.py clear - Clear all records")
