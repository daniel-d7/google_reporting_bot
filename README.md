# Google Reporting Bot

A Python bot that generates daily business reports with automated data quality checks and Google Chat notifications.

## Features

- **Data Quality Check**: Validates data integrity before report generation
- **Automated Report Generation**: Creates visual reports for Country and Manager performance
- **Google Chat Integration**: Sends notifications with success/error status
- **SQLite Logging**: Stores quality check history for comparison
- **Image Generation**: Creates charts and uploads to Google Drive and ImgBB

## Data Quality Check Process

The bot includes a comprehensive data quality check that:

1. **Executes Quality Check Query**: Runs `SQL_QUALITY_CHECK` statement from `.env`
2. **Compares with Last Run**: Checks current NMV against the last run in the same month
3. **First Day Exception**: Allows NMV ≤ last run on the first day of the month
4. **Overwrites Last Run**: Always saves current run as the new "last run" for the month
5. **Error Handling**: Sends error notifications if quality check fails
6. **Success Notification**: Sends completion notification when all processes succeed

### Quality Check Logic

- **Pass Conditions**:
  - No previous run in the current month (first run)
  - Current NMV > Last run NMV
  - Current NMV ≤ Last run NMV BUT it's the first day of the month

- **Fail Conditions**:
  - Current NMV ≤ Last run NMV AND it's NOT the first day of the month

### Quality Check Flow

```
Start → Get Current NMV → Get Last Run (same month) → 
        ↓
Is First Day OR Current > Last? → No → Send Error → Exit
        ↓ Yes
Save Current as Last Run → Generate Reports → Send Success
```

## Environment Variables

Required variables in `.env`:

```properties
# Database Connection
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=5432

# SQL Statements
SQL_QUALITY_CHECK=select * from y4a_sso.agg_quality_check;
SQL_STATEMENT_COUNTRY=select * from y4a_sso.agg_country_perf_mtd;
SQL_STATEMENT_MANAGER=select * from y4a_sso.agg_manager_perf_mtd;
SQL_STATEMENT_PRDLINE=select * from y4a_sso.agg_prdline_perf_mtd;

# Webhooks
WEBHOOK_URL=your_main_notification_webhook
WEBHOOK_URL_LOGGING=your_success_notification_webhook
WEBHOOK_URL_ERROR=your_error_notification_webhook

# API Keys
IMGBB_API_KEY=your_imgbb_api_key

# Google Sheets
SHEET_URL=your_google_sheet_url
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` file with your credentials
4. Place Google service account credentials in `token/` directory
5. Run: `python main.py`

## Testing

Run the test script to verify quality check functionality:
```bash
python test_quality_check.py
```

## Debugging

### Quality Check Database Debug
View the contents of the quality check database:
```bash
python debug_quality_db.py
```

Clear all quality check records:
```bash
python debug_quality_db.py clear
```

### Configuration Validation
Check if all environment variables are properly set:
```bash
python validate_config.py
```

## File Structure

- `main.py` - Main execution script with quality check integration
- `src/quality_check/` - Data quality validation module
- `src/extractor/` - Database and Google Sheets data extraction
- `src/processor/` - Data processing and formatting
- `src/img/` - Image generation and upload utilities
- `src/message/` - Google Chat notification functions
- `token/` - Google service account credentials
- `output/` - Temporary image storage