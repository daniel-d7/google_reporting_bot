import sqlite3
import pandas as pd
import psycopg2
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
import warnings

# Suppress the pandas SQLAlchemy warning since we're now using it properly
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable')

def check_data_quality():
    """
    Check data quality by comparing current NMV with the last run in the same month.
    Returns True if quality check passes, False otherwise.
    """
    load_dotenv()
    
    # Get environment variables
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    sql_quality_check = os.getenv('SQL_QUALITY_CHECK')
    
    if not sql_quality_check:
        raise ValueError("SQL_QUALITY_CHECK environment variable is not set")
    
    # Extract current data from PostgreSQL
    current_data = _extract_quality_data(db_host, db_name, db_user, db_password, db_port, sql_quality_check)
    
    if current_data is None or current_data.empty:
        raise Exception("Failed to extract quality check data from database")
    
    # Get current NMV value
    current_nmv = current_data.iloc[0]['nmv'] if 'nmv' in current_data.columns else None
    
    if current_nmv is None:
        raise Exception("NMV column not found in quality check data")
    
    # Get current date info
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    is_first_day_of_month = current_date.day == 1
    
    # Get the last run from the same month
    last_run = _get_last_run_same_month(current_month)
    
    quality_passed = True
    last_nmv = None
    
    if last_run is not None:
        last_nmv = last_run['nmv']
        
        # Only fail if current <= last AND it's NOT the first day of the month
        if current_nmv <= last_nmv and not is_first_day_of_month:
            quality_passed = False
    
    # Always save the current run data to SQLite (overwrite the last run)
    _save_to_sqlite(current_data)
    
    return quality_passed, current_nmv, last_nmv

def _extract_quality_data(db_host, db_name, db_user, db_password, db_port, sql_statement):
    """Extract quality check data from PostgreSQL using SQLAlchemy"""
    try:
        # Create SQLAlchemy engine
        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(connection_string)
        
        # Use the engine with pandas - this eliminates the warning
        df = pd.read_sql_query(sql_statement, engine)
        return df
        
    except Exception as error:
        print(f"Error extracting quality data: {error}")
        return None

def _save_to_sqlite(data):
    """Save quality check data to SQLite database, overwriting existing data for the current month"""
    # Create SQLite database path from environment variable or fallback to relative path
    from dotenv import load_dotenv
    load_dotenv()
    
    db_path = os.getenv('QUALITY_CHECK_DB')
    if not db_path:
        # Fallback to the original relative path
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'quality_check.db')
    elif not os.path.isabs(db_path):
        # If relative path, make it relative to project root
        project_root = os.getenv('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        db_path = os.path.join(project_root, db_path)
    
    # Add timestamp to data
    data_with_timestamp = data.copy()
    data_with_timestamp['timestamp'] = datetime.now()
    data_with_timestamp['month'] = datetime.now().strftime('%Y-%m')
    
    # Save to SQLite - overwrite existing data for the current month
    with sqlite3.connect(db_path) as conn:
        current_month = datetime.now().strftime('%Y-%m')
        
        # First, try to create the table if it doesn't exist by inserting data
        # This handles the case where the table doesn't exist yet
        try:
            # Check if table exists first
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quality_checks';")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Delete existing records for the current month
                conn.execute("DELETE FROM quality_checks WHERE month = ?", (current_month,))
            
            # Insert new record (this will create the table if it doesn't exist)
            data_with_timestamp.to_sql('quality_checks', conn, if_exists='append', index=False)
            
        except Exception as e:
            print(f"Error saving to SQLite: {e}")
            raise

def _get_last_run_same_month(current_month):
    """Get the last quality check run for the same month"""
    from dotenv import load_dotenv
    load_dotenv()
    
    db_path = os.getenv('QUALITY_CHECK_DB')
    if not db_path:
        # Fallback to the original relative path
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'quality_check.db')
    elif not os.path.isabs(db_path):
        # If relative path, make it relative to project root
        project_root = os.getenv('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        db_path = os.path.join(project_root, db_path)
    
    if not os.path.exists(db_path):
        return None
    
    with sqlite3.connect(db_path) as conn:
        try:
            # First check if table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quality_checks';")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                return None
            
            # Query for the last run in the same month
            query = """
            SELECT * FROM quality_checks 
            WHERE month = ? 
            ORDER BY timestamp DESC
            LIMIT 1
            """
            result = conn.execute(query, (current_month,)).fetchone()
            if result:
                # Get column names
                columns = [description[0] for description in conn.execute(query, (current_month,)).description]
                return dict(zip(columns, result))
            return None
        except sqlite3.OperationalError as e:
            # Handle any database operation errors gracefully
            print(f"Database operation error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error accessing database: {e}")
            return None

def _get_previous_runs(current_month):
    """Get previous quality check runs for the same month (deprecated - use _get_last_run_same_month)"""
    from dotenv import load_dotenv
    load_dotenv()
    
    db_path = os.getenv('QUALITY_CHECK_DB')
    if not db_path:
        # Fallback to the original relative path
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'quality_check.db')
    elif not os.path.isabs(db_path):
        # If relative path, make it relative to project root
        project_root = os.getenv('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        db_path = os.path.join(project_root, db_path)
    
    if not os.path.exists(db_path):
        return pd.DataFrame()
    
    with sqlite3.connect(db_path) as conn:
        query = """
        SELECT * FROM quality_checks 
        WHERE month = ? 
        ORDER BY timestamp
        """
        try:
            return pd.read_sql_query(query, conn, params=(current_month,))
        except:
            # Table doesn't exist yet
            return pd.DataFrame()

def send_error_message(current_nmv, latest_nmv):
    """Send error message to WEBHOOK_URL_ERROR"""
    load_dotenv()
    webhook_url_error = os.getenv('WEBHOOK_URL_ERROR')
    
    if not webhook_url_error:
        raise ValueError("WEBHOOK_URL_ERROR environment variable is not set")
    
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Handle case where values might be 0 (generic error)
    if current_nmv == 0 and latest_nmv == 0:
        error_text = f"🔴 Data quality check failed on {current_date}\n\n" \
                    f"❌ An error occurred during data quality validation.\n" \
                    f"Please check the system logs and investigate the issue."
    else:
        error_text = f"🔴 Data quality check failed on {current_date}\n\n" \
                    f"Current NMV: {current_nmv:,.0f}\n" \
                    f"Last Run NMV: {latest_nmv:,.0f}\n\n" \
                    f"❌ Current NMV is not greater than the last run in the same month.\n" \
                    f"Note: This check is bypassed on the first day of the month.\n" \
                    f"Please investigate the data quality issue."
    
    message = {
        "cardsV2": [
            {
                "card": {
                    "header": {
                        "title": "❌ Data Quality Check Failed"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": error_text
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(webhook_url_error, headers=headers, data=json.dumps(message))
    
    if response.status_code != 200:
        raise Exception(f'Error notification failed: {response.text}')
    
    return "Successfully sent error notification"

def send_success_message():
    """Send success message to WEBHOOK_URL_LOGGING"""
    load_dotenv()
    webhook_url_logging = os.getenv('WEBHOOK_URL_LOGGING')
    
    if not webhook_url_logging:
        raise ValueError("WEBHOOK_URL_LOGGING environment variable is not set")
    
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = {
        "cardsV2": [
            {
                "card": {
                    "header": {
                        "title": "✅ Report Generation Successful"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": f"🟢 Daily report generation completed successfully on {current_date}\n\n"
                                               f"✅ Data quality check: PASSED\n"
                                               f"✅ Report generation: COMPLETED\n"
                                               f"✅ Notifications sent: SUCCESS\n\n"
                                               f"All processes completed without errors."
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(webhook_url_logging, headers=headers, data=json.dumps(message))
    
    if response.status_code != 200:
        raise Exception(f'Success notification failed: {response.text}')
    
    return "Successfully sent success notification"
