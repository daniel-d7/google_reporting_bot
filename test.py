import os
import sqlite3
import pandas as pd

def _get_previous_runs(current_month):
    """Get previous quality check runs for the same month"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'quality_check.db')
    
    with sqlite3.connect(db_path) as conn:
        query = """
        SELECT * FROM quality_checks 
        WHERE month = ? 
        ORDER BY timestamp
        """
        try:
            print(pd.read_sql_query(query, conn, params=(current_month,)))
        except:
            # Table doesn't exist yet
            return pd.DataFrame()