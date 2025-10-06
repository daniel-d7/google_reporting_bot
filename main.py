from src.extractor import extract_from_db, extract_sheets_data, push_dataframe_to_gsheet
from src.processor import pivot_kpi, calc_achievement_vs_target, formatter
from src.img import img_gen_country, img_gen_pic, upload_image, upload_image_gdrive
from src.message import send_notification, send_notification_prdline
from src.quality_check import check_data_quality, send_error_message, send_success_message
import pandas as pd
from time import sleep
from dotenv import load_dotenv
from datetime import datetime
import os
import sys

load_dotenv()

def resolve_path(path_config, fallback_relative_path=""):
    """Resolve absolute path from config, handling both absolute and relative paths"""
    if os.path.isabs(path_config):
        return path_config
    else:
        return os.path.join(project_root, path_config) if path_config else os.path.join(project_root, fallback_relative_path)

# Get configuration from environment variables
project_root = os.getenv('PROJECT_ROOT', os.path.dirname(os.path.abspath(__file__)))
output_dir = os.getenv('OUTPUT_DIR', 'output')
google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
credentials_json = os.getenv('CREDENTIALS_JSON', 'token/credentials.json')
personal_credentials_json = os.getenv('PERSONAL_CREDENTIALS_JSON', 'token/personal_credentials.json')
token_json = os.getenv('TOKEN_JSON', 'token/token.json')
imgbb_api_key = os.getenv('IMGBB_API_KEY')
webhook_url_sso = os.getenv('WEBHOOK_URL_SSO')
webhook_url_cpi = os.getenv('WEBHOOK_URL_CPI')
sheet_url = os.getenv('SHEET_URL')

# Validate required environment variables
required_vars = {
    'GOOGLE_SHEET_ID': google_sheet_id,
    'GDRIVE_FOLDER_ID': gdrive_folder_id,
    'IMGBB_API_KEY': imgbb_api_key,
    'WEBHOOK_URL_SSO': webhook_url_sso,
    'WEBHOOK_URL_CPI': webhook_url_cpi
    }

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Assert that required variables are not None after validation
assert google_sheet_id is not None
assert gdrive_folder_id is not None
assert imgbb_api_key is not None
assert webhook_url_sso is not None
assert webhook_url_cpi is not None

# Data Quality Check - Must pass before proceeding
try:
    print("🔍 Starting data quality check...")
    quality_passed, current_nmv, latest_nmv = check_data_quality()
    
    if not quality_passed:
        print(f"❌ Data quality check failed: Current NMV ({current_nmv:,.0f}) <= Previous NMV ({latest_nmv:,.0f})")
        send_error_message(current_nmv, latest_nmv)
        print("Error notification sent. Exiting...")
        sys.exit(1)
    else:
        print(f"✅ Data quality check passed: Current NMV ({current_nmv:,.0f})")
        
except Exception as e:
    print(f"❌ Data quality check error: {e}")
    # Try to send error message if possible
    try:
        send_error_message(0, 0)  # Send generic error
    except:
        pass
    sys.exit(1)

country_data = extract_from_db(sqlStatement=os.getenv('SQL_STATEMENT_COUNTRY'))
manager_data = extract_from_db(sqlStatement=os.getenv('SQL_STATEMENT_MANAGER'))
prdline_data = extract_from_db(sqlStatement=os.getenv('SQL_STATEMENT_PRDLINE'))

# Check if data extraction was successful
if country_data is None or manager_data is None or prdline_data is None:
    print("❌ Failed to extract data from database")
    try:
        send_error_message(0, 0)  # Send generic error
    except:
        pass
    sys.exit(1)

timestamp = pd.Timestamp.now().strftime('%Y-%m-%d_%H_%M_%S')
country_image_path = os.path.join(resolve_path(output_dir), f"country_data_{timestamp}.png")
manager_image_path = os.path.join(resolve_path(output_dir), f"manager_data_{timestamp}.png")

country_formatted = formatter(country_data)
manager_formatted = formatter(manager_data)

img_gen_country(country_formatted, country_image_path)
img_gen_pic(manager_formatted, manager_image_path)

credentials_path = resolve_path(credentials_json)
push_dataframe_to_gsheet(prdline_data, google_sheet_id, 'raw', credentials_path)

url_thumbnail_country = upload_image(country_image_path, imgbb_api_key)
personal_creds_path = resolve_path(personal_credentials_json)
token_path = resolve_path(token_json)
url_zoom_country = upload_image_gdrive(country_image_path, personal_creds_path, token_path, folder_id=gdrive_folder_id)

sleep(10)


url_thumbnail_manager = upload_image(manager_image_path, imgbb_api_key)
url_zoom_manager = upload_image_gdrive(manager_image_path, personal_creds_path, token_path, folder_id=gdrive_folder_id)

sleep(10)

current_date = datetime.now().strftime('%Y-%m-%d')

country_message = f"📊 Báo cáo tiến độ kinh doanh theo Country ngày {current_date}:"
send_notification(country_message, url_thumbnail_country, url_zoom_country, webhook_url_sso)
send_notification(country_message, url_thumbnail_country, url_zoom_country, webhook_url_cpi)
sleep(5)

manager_message = f"📊 Báo cáo tiến độ kinh doanh theo Manager ngày {current_date}:"
send_notification(manager_message, url_thumbnail_manager, url_zoom_manager, webhook_url_sso)
send_notification(manager_message, url_thumbnail_manager, url_zoom_manager, webhook_url_cpi)
sleep(5)

productline_message = f"📊 Dữ liệu chi tiết theo Product Line ngày {current_date}\nLưu ý: Số liệu sẽ được overwrite theo ngày."
send_notification_prdline(productline_message, sheet_url, webhook_url_sso)
send_notification_prdline(productline_message, sheet_url, webhook_url_cpi)
sleep(5)

output_folder_path = resolve_path(output_dir)

for item in os.listdir(output_folder_path):
    if item.endswith(".png"):
        if os.path.isfile(item_path := os.path.join(output_folder_path, item)):
            os.remove(item_path)

# Send success notification after all processes complete
try:
    print("📧 Sending success notification...")
    send_success_message()
    print("✅ Success notification sent successfully!")
except Exception as e:
    print(f"⚠️ Warning: Failed to send success notification: {e}")
    # Don't exit on success notification failure, as the main process completed