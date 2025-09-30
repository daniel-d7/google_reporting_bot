"""Database data extraction module."""
import pandas as pd
from typing import Optional
from sqlalchemy import create_engine

from ..config import get_settings
from ..utils import get_logger


logger = get_logger(__name__)


def extract_from_db(sqlStatement: str) -> Optional[pd.DataFrame]:
    """
    Extract data from PostgreSQL database using SQLAlchemy.
    
    Args:
        sqlStatement: SQL query to execute
        
    Returns:
        DataFrame with query results or None if error occurs
    """
    settings = get_settings()
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(settings.db_connection_string)
        
        # Use the engine with pandas
        df = pd.read_sql_query(sqlStatement, engine)
        logger.info(f"Data extracted successfully: {len(df)} rows")
        
        # Cleanup
        engine.dispose()
        
        return df
        
    except Exception as error:
        logger.error(f"Error extracting data from database: {error}")
        return None
