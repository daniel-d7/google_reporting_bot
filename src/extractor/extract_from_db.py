import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import warnings

# Suppress the pandas SQLAlchemy warning since we're now using it properly
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable')

def extract_from_db(sqlStatement):
    """Extract data from PostgreSQL database using SQLAlchemy"""
    load_dotenv()
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')

    try:
        # Create SQLAlchemy engine
        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(connection_string)
        
        # Use the engine with pandas - this eliminates the warning
        df = pd.read_sql_query(sqlStatement, engine)
        print("Data extracted successfully.")
        return df
        
    except Exception as error:
        print(f"Error connecting: {error}")
        return None