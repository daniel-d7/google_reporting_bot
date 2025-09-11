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

imgbb_api_key = os.getenv('IMGBB_API_KEY')
webhook_url = os.getenv('WEBHOOK_URL')

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
country_image_path = fr"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\output\country_data_{timestamp}.png"
manager_image_path = fr"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\output\manager_data_{timestamp}.png"

country_formatted = formatter(country_data)
manager_formatted = formatter(manager_data)

img_gen_country(country_formatted, country_image_path)
img_gen_pic(manager_formatted, manager_image_path)

push_dataframe_to_gsheet(prdline_data, '1shAfxhGXdRu_kgKQg9cst307tpuJoawzkG2_bcMD7-4', 'raw', r"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\token\credentials.json")

url_thumbnail_country = upload_image(country_image_path, imgbb_api_key)
url_zoom_country = upload_image_gdrive(country_image_path, r"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\token\personal_credentials.json", r"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\token\token.json", folder_id='1LR2Z-YP6uvuWB8xMSoooPf9GDf8UVoYG')

sleep(10)


url_thumbnail_manager = upload_image(manager_image_path, imgbb_api_key)
url_zoom_manager = upload_image_gdrive(manager_image_path, r"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\token\personal_credentials.json", r"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\token\token.json", folder_id='1LR2Z-YP6uvuWB8xMSoooPf9GDf8UVoYG')

sleep(10)

current_date = datetime.now().strftime('%Y-%m-%d')

country_message = f"📊 Báo cáo tiến độ kinh doanh theo Country ngày {current_date}:"
send_notification(country_message, url_thumbnail_country, url_zoom_country, webhook_url)
sleep(5)

manager_message = f"📊 Báo cáo tiến độ kinh doanh theo Manager ngày {current_date}:"
send_notification(manager_message, url_thumbnail_manager, url_zoom_manager, webhook_url)
sleep(5)

sheets = "https://docs.google.com/spreadsheets/d/1shAfxhGXdRu_kgKQg9cst307tpuJoawzkG2_bcMD7-4/edit"
productline_message = f"📊 Dữ liệu chi tiết theo Product Line ngày {current_date}\nLưu ý: Số liệu sẽ được overwrite theo ngày."
send_notification_prdline(productline_message, sheets, webhook_url)
sleep(5)

folder_path = fr"C:\Users\cuongdq\Documents\LAB\Github\google_reporting_bot\output"

for item in os.listdir(folder_path):
    if item.endswith(".png"):
        if os.path.isfile(item_path := os.path.join(folder_path, item)):
            os.remove(item_path)

# Send success notification after all processes complete
try:
    print("📧 Sending success notification...")
    send_success_message()
    print("✅ Success notification sent successfully!")
except Exception as e:
    print(f"⚠️ Warning: Failed to send success notification: {e}")
    # Don't exit on success notification failure, as the main process completed