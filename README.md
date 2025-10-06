# 📊 Google Reporting Bot

An automated Python bot that generates daily business intelligence reports with integrated data quality validation and real-time notifications. The bot extracts data from PostgreSQL databases and Google Sheets, performs quality checks, generates visual reports, and delivers them through Google Chat.

## ✨ Key Features

### 🔍 **Data Quality Assurance**
- Automated data integrity validation before report generation
- Month-over-month NMV (Net Merchandise Value) comparison
- SQLite-based quality check history and logging
- Configurable validation rules with first-day-of-month exceptions

### 📈 **Intelligent Report Generation**
- Multi-dimensional performance reports (Country, Manager, Product Line)
- Automated chart generation with matplotlib
- Pivot table processing and KPI calculations
- Achievement vs. target analysis

### 🔗 **Multi-Platform Integration**
- **Google Chat**: Real-time success/error notifications via webhooks  
- **Google Drive**: Automated image upload and sharing
- **Google Sheets**: Bidirectional data synchronization
- **ImgBB**: Alternative image hosting service

### 🗄️ **Data Sources**
- PostgreSQL database connectivity
- Google Sheets integration
- Local SQLite quality check database

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```properties
# 🗄️ Database Connection
DB_HOST=your_postgresql_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_PORT=5432

# 📊 SQL Query Statements
SQL_QUALITY_CHECK=select * from y4a_sso.agg_quality_check;
SQL_STATEMENT_COUNTRY=select * from y4a_sso.agg_country_perf_mtd;
SQL_STATEMENT_MANAGER=select * from y4a_sso.agg_manager_perf_mtd;
SQL_STATEMENT_PRDLINE=select * from y4a_sso.agg_prdline_perf_mtd;

# 🔔 Google Chat Webhooks
WEBHOOK_URL=your_main_notification_webhook_url
WEBHOOK_URL_LOGGING=your_success_notification_webhook_url
WEBHOOK_URL_ERROR=your_error_notification_webhook_url

# 🔑 API Keys
IMGBB_API_KEY=your_imgbb_api_key

# 📋 Google Sheets Integration
SHEET_URL=your_google_sheet_url
GOOGLE_SHEET_ID=your_google_sheet_id

# 📁 Google Drive Configuration
GDRIVE_FOLDER_ID=your_google_drive_folder_id

# 📂 File Paths (Optional - uses defaults if not specified)
PROJECT_ROOT=/path/to/project
OUTPUT_DIR=output
CREDENTIALS_JSON=token/credentials.json
PERSONAL_CREDENTIALS_JSON=token/personal_credentials.json
TOKEN_JSON=token/token.json
```

### Google Service Account Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Required APIs**
   - Google Sheets API
   - Google Drive API
   - Gmail API (if email notifications are needed)

3. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Download the JSON credentials file

4. **Configure Credentials**
   - Place the JSON file in `token/credentials.json`
   - For personal Google account access, place OAuth credentials in `token/personal_credentials.json`

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+ 
- PostgreSQL database access
- Google Cloud Platform account
- Google Chat workspace (for notifications)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/daniel-d7/google_reporting_bot.git
   cd google_reporting_bot
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Use your preferred text editor
   ```

4. **Set Up Google Credentials**
   ```bash
   # Create token directory
   mkdir token
   
   # Place your Google service account JSON file
   # token/credentials.json
   ```

5. **Run the Application**
   ```bash
   python main.py
   ```

## 🧪 Testing & Validation

### Quality Check Testing
Verify the data quality validation system:
```bash
python test_quality_check.py
```

### Configuration Validation
Ensure all environment variables are properly configured:
```bash
python validate_config.py
```

### Database Connection Test
Test PostgreSQL database connectivity:
```bash
python -c "from src.extractor.extract_from_db import test_connection; test_connection()"
```

## 🐛 Debugging & Troubleshooting

### Quality Check Database Debug

**View quality check history:**
```bash
python debug_quality_db.py
```

**Clear all quality check records:**
```bash
python debug_quality_db.py clear
```

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Database Connection** | `psycopg2.OperationalError` | Verify DB credentials in `.env` |
| **Google Auth** | `google.auth.exceptions.RefreshError` | Regenerate service account JSON |
| **Webhook Failure** | Notifications not sent | Check webhook URLs and permissions |
| **Image Upload** | Upload failures | Verify API keys and folder permissions |

### Logging

The bot generates detailed logs for troubleshooting:
- Quality check results are stored in `quality_check.db`
- Runtime logs are output to console
- Error notifications are sent via configured webhooks

## 📁 Project Structure

```
google_reporting_bot/
├── 📄 main.py                    # Main execution script
├── 📋 requirements.txt           # Python dependencies
├── 🗃️ quality_check.db          # SQLite quality check database
├── 📖 README.md                  # This documentation
├── 📂 src/                       # Source code modules
│   ├── 🔍 quality_check/        # Data validation system
│   │   ├── __init__.py
│   │   └── quality_check.py
│   ├── 📊 extractor/             # Data extraction utilities
│   │   ├── __init__.py
│   │   ├── extract_from_db.py
│   │   └── extract_from_gsheet.py
│   ├── ⚙️ processor/             # Data processing engine
│   │   ├── __init__.py
│   │   └── processor.py
│   ├── 🖼️ img/                   # Image generation & upload
│   │   ├── __init__.py
│   │   ├── img_gen.py
│   │   ├── img_upload.py
│   │   └── img_upload_gdrive.py
│   └── 💬 message/               # Notification system
│       ├── __init__.py
│       └── send_message.py
├── 🔐 token/                     # Google service credentials
│   ├── credentials.json
│   ├── personal_credentials.json
│   └── token.json
└── 📁 output/                    # Temporary image storage
```

### Module Responsibilities

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `quality_check` | Data validation and integrity checks | `check_data_quality()`, `send_error_message()` |
| `extractor` | Data retrieval from various sources | `extract_from_db()`, `extract_sheets_data()` |
| `processor` | Data transformation and analysis | `pivot_kpi()`, `calc_achievement_vs_target()` |
| `img` | Chart generation and image management | `img_gen_country()`, `upload_image_gdrive()` |
| `message` | Communication and notifications | `send_notification()`, `send_notification_prdline()` |

## 🔧 Advanced Configuration

### Scheduling Automation

**Using cron (Linux/macOS):**
```bash
# Run daily at 8:00 AM
0 8 * * * /path/to/venv/bin/python /path/to/google_reporting_bot/main.py

# Run every weekday at 9:30 AM
30 9 * * 1-5 /path/to/venv/bin/python /path/to/google_reporting_bot/main.py
```

**Using Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Set action to start `python.exe` with argument `main.py`
5. Set start directory to project folder

### Performance Optimization

- **Database Connection Pooling**: Configure connection pools for high-frequency runs
- **Caching**: Implement Redis caching for frequently accessed data
- **Async Processing**: Use asyncio for concurrent API calls
- **Resource Monitoring**: Monitor memory usage for large datasets