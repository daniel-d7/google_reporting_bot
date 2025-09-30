"""Data quality check module."""
import sqlite3
import pandas as pd
import requests
import json
import os
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from sqlalchemy import create_engine

from ..config import get_settings
from ..utils import get_logger


logger = get_logger(__name__)


def check_data_quality() -> Tuple[bool, float, Optional[float]]:
    """
    Check data quality by comparing current NMV with the last run in the same month.
    
    Returns:
        Tuple of (quality_passed, current_nmv, last_nmv)
        
    Raises:
        Exception: If quality check fails
    """
    settings = get_settings()
    
    if not settings.sql_quality_check:
        raise ValueError("SQL_QUALITY_CHECK environment variable is not set")
    
    # Extract current data from PostgreSQL
    current_data = _extract_quality_data(settings.sql_quality_check)
    
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
            logger.warning(
                f"Quality check failed: Current NMV ({current_nmv:,.0f}) "
                f"<= Last NMV ({last_nmv:,.0f}) on day {current_date.day}"
            )
    else:
        logger.info("No previous run found for current month - quality check passed")
    
    # Always save the current run data to SQLite (overwrite the last run)
    _save_to_sqlite(current_data)
    
    return quality_passed, current_nmv, last_nmv


def _extract_quality_data(sql_statement: str) -> Optional[pd.DataFrame]:
    """
    Extract quality check data from PostgreSQL using SQLAlchemy.
    
    Args:
        sql_statement: SQL query to execute
        
    Returns:
        DataFrame with quality data or None if error
    """
    settings = get_settings()
    
    try:
        engine = create_engine(settings.db_connection_string)
        df = pd.read_sql_query(sql_statement, engine)
        engine.dispose()
        
        logger.info(f"Extracted quality data: {len(df)} rows")
        return df
        
    except Exception as error:
        logger.error(f"Error extracting quality data: {error}")
        return None


def _save_to_sqlite(data: pd.DataFrame) -> None:
    """
    Save quality check data to SQLite database, overwriting existing data for the current month.
    
    Args:
        data: DataFrame to save
    """
    settings = get_settings()
    db_path = settings.quality_check_db_path
    
    # Add timestamp to data
    data_with_timestamp = data.copy()
    data_with_timestamp['timestamp'] = datetime.now()
    data_with_timestamp['month'] = datetime.now().strftime('%Y-%m')
    
    # Save to SQLite - overwrite existing data for the current month
    try:
        with sqlite3.connect(db_path) as conn:
            current_month = datetime.now().strftime('%Y-%m')
            
            # Check if table exists first
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='quality_checks';"
            )
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Delete existing records for the current month
                conn.execute("DELETE FROM quality_checks WHERE month = ?", (current_month,))
                logger.info(f"Deleted existing quality check records for {current_month}")
            
            # Insert new record (this will create the table if it doesn't exist)
            data_with_timestamp.to_sql('quality_checks', conn, if_exists='append', index=False)
            logger.info(f"Saved quality check data for {current_month}")
            
    except Exception as e:
        logger.error(f"Error saving to SQLite: {e}")
        raise


def _get_last_run_same_month(current_month: str) -> Optional[Dict[str, Any]]:
    """
    Get the last quality check run for the same month.
    
    Args:
        current_month: Month string in format 'YYYY-MM'
        
    Returns:
        Dictionary with last run data or None if not found
    """
    settings = get_settings()
    db_path = settings.quality_check_db_path
    
    if not os.path.exists(db_path):
        logger.info(f"Quality check database not found: {db_path}")
        return None
    
    try:
        with sqlite3.connect(db_path) as conn:
            # First check if table exists
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='quality_checks';"
            )
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                logger.info("Quality checks table does not exist yet")
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
                columns = [description[0] for description in 
                          conn.execute(query, (current_month,)).description]
                last_run = dict(zip(columns, result))
                logger.info(f"Found last run for {current_month}: NMV = {last_run.get('nmv', 'N/A')}")
                return last_run
            
            logger.info(f"No previous run found for {current_month}")
            return None
            
    except sqlite3.OperationalError as e:
        logger.error(f"Database operation error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error accessing database: {e}")
        return None


def send_error_message(current_nmv: float, latest_nmv: float) -> str:
    """
    Send error message to webhook.
    
    Args:
        current_nmv: Current NMV value
        latest_nmv: Latest NMV value
        
    Returns:
        Success message
        
    Raises:
        Exception: If notification fails
    """
    settings = get_settings()
    
    if not settings.webhook_url_error:
        raise ValueError("WEBHOOK_URL_ERROR environment variable is not set")
    
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Handle case where values might be 0 (generic error)
    if current_nmv == 0 and latest_nmv == 0:
        error_text = (
            f"🔴 Data quality check failed on {current_date}\n\n"
            f"❌ An error occurred during data quality validation.\n"
            f"Please check the system logs and investigate the issue."
        )
    else:
        error_text = (
            f"🔴 Data quality check failed on {current_date}\n\n"
            f"Current NMV: {current_nmv:,.0f}\n"
            f"Last Run NMV: {latest_nmv:,.0f}\n\n"
            f"❌ Current NMV is not greater than the last run in the same month.\n"
            f"Note: This check is bypassed on the first day of the month.\n"
            f"Please investigate the data quality issue."
        )
    
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
    response = requests.post(
        settings.webhook_url_error,
        headers=headers,
        data=json.dumps(message)
    )
    
    if response.status_code != 200:
        raise Exception(f'Error notification failed: {response.text}')
    
    logger.info("Error notification sent successfully")
    return "Successfully sent error notification"


def send_success_message() -> str:
    """
    Send success message to webhook.
    
    Returns:
        Success message
        
    Raises:
        Exception: If notification fails
    """
    settings = get_settings()
    
    if not settings.webhook_url_logging:
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
                                        "text": (
                                            f"🟢 Daily report generation completed successfully on {current_date}\n\n"
                                            f"✅ Data quality check: PASSED\n"
                                            f"✅ Report generation: COMPLETED\n"
                                            f"✅ Notifications sent: SUCCESS\n\n"
                                            f"All processes completed without errors."
                                        )
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
    response = requests.post(
        settings.webhook_url_logging,
        headers=headers,
        data=json.dumps(message)
    )
    
    if response.status_code != 200:
        raise Exception(f'Success notification failed: {response.text}')
    
    logger.info("Success notification sent successfully")
    return "Successfully sent success notification"
