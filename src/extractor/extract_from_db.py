import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

def extract_from_db(sqlStatement):
    load_dotenv()
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    connection = None

    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = connection.cursor()
        cursor.execute(sqlStatement)
        # Fetch column headers
        headers = [desc[0] for desc in cursor.description]
        # Fetch all rows
        data = cursor.fetchall()
        # Create Pandas DataFrame
        df = pd.DataFrame(data, columns=headers)
        return df
    except (Exception, psycopg2.Error) as error:
        print(f"Error connecting: {error}")
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")