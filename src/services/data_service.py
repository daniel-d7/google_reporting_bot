"""Data extraction and processing service."""
import pandas as pd
from typing import Optional
from sqlalchemy import create_engine

from ..config import Settings
from ..utils import get_logger


logger = get_logger(__name__)


class DataService:
    """Service for data extraction and manipulation."""
    
    def __init__(self, settings: Settings):
        """
        Initialize data service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.engine = create_engine(settings.db_connection_string)
    
    def extract_from_db(self, sql_statement: str) -> Optional[pd.DataFrame]:
        """
        Extract data from PostgreSQL database.
        
        Args:
            sql_statement: SQL query to execute
            
        Returns:
            DataFrame with query results or None if error
        """
        try:
            df = pd.read_sql_query(sql_statement, self.engine)
            logger.info(f"Successfully extracted {len(df)} rows from database")
            return df
        except Exception as error:
            logger.error(f"Error extracting data from database: {error}")
            return None
    
    def extract_country_data(self) -> Optional[pd.DataFrame]:
        """Extract country data from database."""
        logger.info("Extracting country data...")
        return self.extract_from_db(self.settings.sql_statement_country)
    
    def extract_manager_data(self) -> Optional[pd.DataFrame]:
        """Extract manager data from database."""
        logger.info("Extracting manager data...")
        return self.extract_from_db(self.settings.sql_statement_manager)
    
    def extract_product_line_data(self) -> Optional[pd.DataFrame]:
        """Extract product line data from database."""
        logger.info("Extracting product line data...")
        return self.extract_from_db(self.settings.sql_statement_prdline)
    
    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'engine'):
            self.engine.dispose()
