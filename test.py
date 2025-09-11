import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

def _get_previous_runs(current_month):
    """Get previous quality check runs for the same month"""
    load_dotenv()
    
    # Get database path from environment variable or fallback to relative path
    db_path = os.getenv('QUALITY_CHECK_DB')
    if not db_path:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'quality_check.db')
    elif not os.path.isabs(db_path):
        # If relative path, make it relative to project root
        project_root = os.getenv('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        db_path = os.path.join(project_root, db_path)
    
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