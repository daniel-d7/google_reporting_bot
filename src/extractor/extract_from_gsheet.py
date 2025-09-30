"""Google Sheets data extraction and upload module."""
from google.oauth2.service_account import Credentials
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe

from ..utils import get_logger


logger = get_logger(__name__)


def extract_sheets_data(credentials_file: str, sheet_url: str) -> pd.DataFrame:
    """
    Extract data from Google Sheets.
    
    Args:
        credentials_file: Path to Google service account credentials JSON
        sheet_url: URL of the Google Sheet
        
    Returns:
        DataFrame with sheet data
        
    Raises:
        Exception: If extraction fails or sheet is empty
    """
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(sheet_url).worksheet('raw')
        data = sheet.get_all_values()
        
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            df = pd.DataFrame()
        
        if df.empty:
            raise Exception("No data extracted from Google Sheets")
        
        logger.info(f"Extracted {len(df)} rows from Google Sheets")
        return df
        
    except Exception as e:
        logger.error(f"Error extracting from Google Sheets: {e}")
        raise


def push_dataframe_to_gsheet(
    df: pd.DataFrame, 
    spreadsheet_id: str, 
    sheet_name: str, 
    creds_json_path: str
) -> None:
    """
    Push DataFrame to Google Sheets.
    
    Args:
        df: DataFrame to upload
        spreadsheet_id: Google Spreadsheet ID
        sheet_name: Name of the sheet/tab
        creds_json_path: Path to Google service account credentials JSON
        
    Raises:
        Exception: If upload fails
    """
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(creds_json_path, scopes=scopes)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=sheet_name, 
                rows=df.shape[0] + 10, 
                cols=df.shape[1] + 10
            )
        
        set_with_dataframe(worksheet, df)
        
        logger.info(
            f"DataFrame pushed to sheet '{sheet_name}' "
            f"in spreadsheet '{spreadsheet_id}' successfully"
        )
        
    except Exception as e:
        logger.error(f"Error pushing DataFrame to Google Sheets: {e}")
        raise
