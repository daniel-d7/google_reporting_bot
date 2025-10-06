from google.oauth2.service_account import Credentials
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe


def extract_sheets_data(credentials_file, sheet_url):
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
            
        return df
            
    except Exception as e:
        raise

def push_dataframe_to_gsheet(df: pd.DataFrame, spreadsheet_id: str, sheet_name: str, creds_json_path: str):

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds  = Credentials.from_service_account_file(creds_json_path, scopes=scopes)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=str(df.shape[0] + 10), cols=str(df.shape[1] + 10))

    set_with_dataframe(worksheet, df)

    print(f"DataFrame pushed to sheet '{sheet_name}' in spreadsheet '{spreadsheet_id}' successfully.")