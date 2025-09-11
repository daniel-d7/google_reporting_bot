#!/usr/bin/env python3
"""
Configuration validation script for Google Reporting Bot
Checks if all required environment variables are properly set
"""

import os
from dotenv import load_dotenv

def validate_config():
    """Validate all required environment variables"""
    load_dotenv()
    
    required_vars = [
        'DB_HOST',
        'DB_NAME', 
        'DB_USER',
        'DB_PASSWORD',
        'DB_PORT',
        'SQL_QUALITY_CHECK',
        'SQL_STATEMENT_COUNTRY',
        'SQL_STATEMENT_MANAGER',
        'SQL_STATEMENT_PRDLINE',
        'WEBHOOK_URL',
        'WEBHOOK_URL_LOGGING',
        'WEBHOOK_URL_ERROR',
        'IMGBB_API_KEY',
        'SHEET_URL'
    ]
    
    print("🔍 Validating configuration...")
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Mask sensitive values for display
            if 'PASSWORD' in var or 'KEY' in var or 'WEBHOOK' in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars:
        print(f"\n❌ Configuration validation failed!")
        print(f"Missing variables: {', '.join(missing_vars)}")
        return False
    else:
        print(f"\n✅ Configuration validation passed!")
        print(f"All {len(required_vars)} required variables are set.")
        return True

if __name__ == "__main__":
    validate_config()
