# Google Reporting Bot

A Python bot that generates daily business reports with automated data quality checks and Google Chat notifications.

## 🌟 Features

- **Data Quality Check**: Validates data integrity before report generation
- **Automated Report Generation**: Creates visual reports for Country and Manager performance
- **Google Chat Integration**: Sends notifications with success/error status
- **SQLite Logging**: Stores quality check history for comparison
- **Image Generation**: Creates charts and uploads to Google Drive and ImgBB
- **Service-Oriented Architecture**: Clean, modular, and maintainable code structure
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📁 Project Structure

```
google_reporting_bot/
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── quality_check.db            # SQLite database for quality checks
├── output/                     # Generated report images (temporary)
├── token/                      # Google API credentials
│   ├── credentials.json
│   ├── personal_credentials.json
│   └── token.json
└── src/                        # Source code
    ├── config/                 # Configuration management
    │   ├── __init__.py
    │   └── settings.py         # Settings class with validation
    ├── services/               # Business logic services
    │   ├── __init__.py
    │   ├── data_service.py     # Data extraction
    │   ├── report_service.py   # Report generation
    │   ├── notification_service.py  # Notifications
    │   └── quality_service.py  # Quality checks
    ├── extractor/              # Data extraction modules
    │   ├── __init__.py
    │   ├── extract_from_db.py  # Database extraction
    │   └── extract_from_gsheet.py  # Google Sheets
    ├── processor/              # Data processing
    │   ├── __init__.py
    │   └── processor.py        # Data formatting
    ├── img/                    # Image handling
    │   ├── __init__.py
    │   ├── img_gen.py          # Image generation
    │   ├── img_upload.py       # ImgBB upload
    │   └── img_upload_gdrive.py  # Google Drive upload
    ├── message/                # Messaging
    │   ├── __init__.py
    │   └── send_message.py     # Google Chat messages
    ├── quality_check/          # Quality validation
    │   ├── __init__.py
    │   └── quality_check.py    # Quality check logic
    └── utils/                  # Utilities
        ├── __init__.py
        └── logger.py           # Logging configuration
```

## 🏗️ Architecture

### Service Layer
The application uses a service-oriented architecture with the following services:

- **DataService**: Handles all database interactions and data extraction
- **ReportService**: Manages report generation, formatting, and image creation
- **NotificationService**: Sends notifications to Google Chat webhooks
- **QualityService**: Performs data quality validation and sends status notifications

### Configuration Management
- Centralized configuration in `src/config/settings.py`
- Environment variable validation on startup
- Path resolution for cross-platform compatibility

### Logging
- Structured logging throughout the application
- Log levels: INFO, WARNING, ERROR
- Console output with timestamps

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Google Cloud Project with:
  - Google Sheets API enabled
  - Google Drive API enabled
  - Service account credentials
- ImgBB API account
- Google Chat webhooks

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd google_reporting_bot
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configurations
```

5. **Set up Google credentials**
- Place your Google service account credentials in `token/credentials.json`
- Place your personal OAuth credentials in `token/personal_credentials.json`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

#### Database Configuration
```properties
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_PORT=5432
```

#### SQL Statements
```properties
SQL_STATEMENT_COUNTRY=SELECT ... FROM ... WHERE ...
SQL_STATEMENT_MANAGER=SELECT ... FROM ... WHERE ...
SQL_STATEMENT_PRDLINE=SELECT ... FROM ... WHERE ...
SQL_QUALITY_CHECK=SELECT nmv FROM ... WHERE ...
```

#### Google Services
```properties
GOOGLE_SHEET_ID=your_sheet_id
GDRIVE_FOLDER_ID=your_folder_id
CREDENTIALS_JSON=token/credentials.json
PERSONAL_CREDENTIALS_JSON=token/personal_credentials.json
TOKEN_JSON=token/token.json
SHEET_URL=https://docs.google.com/spreadsheets/d/...
```

#### Image Hosting
```properties
IMGBB_API_KEY=your_imgbb_api_key
```

#### Webhook URLs
```properties
WEBHOOK_URL_SSO=https://chat.googleapis.com/v1/spaces/.../messages?key=...
WEBHOOK_URL_CPI=https://chat.googleapis.com/v1/spaces/.../messages?key=...
WEBHOOK_URL_ERROR=https://chat.googleapis.com/v1/spaces/.../messages?key=...
WEBHOOK_URL_LOGGING=https://chat.googleapis.com/v1/spaces/.../messages?key=...
```

## 🎯 Usage

### Run the bot
```bash
python main.py
```

### Expected Output
```
================================================================================
Starting Google Reporting Bot
================================================================================
2025-09-30 10:00:00 - google_reporting_bot - INFO - Configuration loaded and validated successfully
--------------------------------------------------------------------------------
STEP 1: Data Quality Check
--------------------------------------------------------------------------------
2025-09-30 10:00:01 - google_reporting_bot - INFO - Starting data quality check...
2025-09-30 10:00:02 - google_reporting_bot - INFO - Data quality check passed: Current NMV (1,234,567)
--------------------------------------------------------------------------------
STEP 2: Extract Data from Database
--------------------------------------------------------------------------------
...
```

## 📊 Data Quality Check Process

The bot includes a comprehensive data quality check that:

1. **Executes Quality Check Query**: Runs `SQL_QUALITY_CHECK` statement from `.env`
2. **Compares with Last Run**: Checks current NMV against the last run in the same month
3. **First Day Exception**: Allows NMV ≤ last run on the first day of the month
4. **Overwrites Last Run**: Always saves current run as the new "last run" for the month
5. **Error Handling**: Sends error notifications if quality check fails
6. **Success Notification**: Sends completion notification when all processes succeed

### Quality Check Logic

**Pass Conditions:**
- No previous run in the current month (first run)
- Current NMV > Last run NMV
- Current NMV ≤ Last run NMV BUT it's the first day of the month

**Fail Conditions:**
- Current NMV ≤ Last run NMV AND it's NOT the first day of the month

### Quality Check Flow

```
Start → Get Current NMV → Get Last Run (same month)
        ↓
Is First Day OR Current > Last? → No → Send Error → Exit
        ↓ Yes
Save Current as Last Run → Generate Reports → Send Success
```

## 🔧 Development

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Adding New Features

1. **Add a new service**: Create a new file in `src/services/`
2. **Add configuration**: Update `src/config/settings.py`
3. **Update main.py**: Import and use the new service
4. **Add tests**: (Future enhancement)

### Logging

Use the logger in your modules:
```python
from ..utils import get_logger

logger = get_logger(__name__)

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

## 🐛 Troubleshooting

### Common Issues

**Missing environment variables**
```
Error: Missing required environment variables: GOOGLE_SHEET_ID, IMGBB_API_KEY
Solution: Check your .env file and ensure all required variables are set
```

**Database connection failed**
```
Error: Error extracting data from database
Solution: Verify database credentials and network connectivity
```

**Google API authentication failed**
```
Error: Google Drive upload failed
Solution: Check your credentials.json and ensure APIs are enabled
```

## 📝 License

[Add your license here]

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

[Add your contact information here]

## 🙏 Acknowledgments

- Google Cloud Platform for APIs
- ImgBB for image hosting
- The Python community

---

**Note**: This is a refactored version with improved architecture, better error handling, comprehensive logging, and service-oriented design for maintainability and scalability.

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