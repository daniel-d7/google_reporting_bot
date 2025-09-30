"""Configuration management module."""
import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        """Initialize settings by loading environment variables."""
        load_dotenv()
        
        # Project paths
        self.project_root = os.getenv('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.output_dir = os.getenv('OUTPUT_DIR', 'output')
        
        # Database configuration
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_port = os.getenv('DB_PORT', '5432')
        
        # SQL statements
        self.sql_statement_country = os.getenv('SQL_STATEMENT_COUNTRY')
        self.sql_statement_manager = os.getenv('SQL_STATEMENT_MANAGER')
        self.sql_statement_prdline = os.getenv('SQL_STATEMENT_PRDLINE')
        self.sql_quality_check = os.getenv('SQL_QUALITY_CHECK')
        
        # Google services
        self.google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
        self.credentials_json = os.getenv('CREDENTIALS_JSON', 'token/credentials.json')
        self.personal_credentials_json = os.getenv('PERSONAL_CREDENTIALS_JSON', 'token/personal_credentials.json')
        self.token_json = os.getenv('TOKEN_JSON', 'token/token.json')
        self.sheet_url = os.getenv('SHEET_URL')
        
        # Image hosting
        self.imgbb_api_key = os.getenv('IMGBB_API_KEY')
        
        # Webhook URLs
        self.webhook_url_sso = os.getenv('WEBHOOK_URL_SSO')
        self.webhook_url_cpi = os.getenv('WEBHOOK_URL_CPI')
        self.webhook_url_error = os.getenv('WEBHOOK_URL_ERROR')
        self.webhook_url_logging = os.getenv('WEBHOOK_URL_LOGGING')
        
        # Quality check database
        self.quality_check_db = os.getenv('QUALITY_CHECK_DB', 'quality_check.db')
        
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate that all required environment variables are set.
        
        Returns:
            Tuple of (is_valid, missing_variables)
        """
        required_vars = {
            'DB_HOST': self.db_host,
            'DB_NAME': self.db_name,
            'DB_USER': self.db_user,
            'DB_PASSWORD': self.db_password,
            'GOOGLE_SHEET_ID': self.google_sheet_id,
            'GDRIVE_FOLDER_ID': self.gdrive_folder_id,
            'IMGBB_API_KEY': self.imgbb_api_key,
            'WEBHOOK_URL_SSO': self.webhook_url_sso,
            'WEBHOOK_URL_CPI': self.webhook_url_cpi,
            'WEBHOOK_URL_ERROR': self.webhook_url_error,
            'WEBHOOK_URL_LOGGING': self.webhook_url_logging,
            'SQL_STATEMENT_COUNTRY': self.sql_statement_country,
            'SQL_STATEMENT_MANAGER': self.sql_statement_manager,
            'SQL_STATEMENT_PRDLINE': self.sql_statement_prdline,
            'SQL_QUALITY_CHECK': self.sql_quality_check,
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        return len(missing_vars) == 0, missing_vars
    
    def resolve_path(self, path_config: str, fallback_relative_path: str = "") -> str:
        """
        Resolve absolute path from config, handling both absolute and relative paths.
        
        Args:
            path_config: Path from configuration
            fallback_relative_path: Fallback path if path_config is empty
            
        Returns:
            Absolute path
        """
        if os.path.isabs(path_config):
            return path_config
        else:
            return os.path.join(self.project_root, path_config) if path_config else os.path.join(self.project_root, fallback_relative_path)
    
    @property
    def db_connection_string(self) -> str:
        """Get database connection string for SQLAlchemy."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def output_path(self) -> str:
        """Get absolute path to output directory."""
        return self.resolve_path(self.output_dir)
    
    @property
    def credentials_path(self) -> str:
        """Get absolute path to credentials JSON file."""
        return self.resolve_path(self.credentials_json)
    
    @property
    def personal_credentials_path(self) -> str:
        """Get absolute path to personal credentials JSON file."""
        return self.resolve_path(self.personal_credentials_json)
    
    @property
    def token_path(self) -> str:
        """Get absolute path to token JSON file."""
        return self.resolve_path(self.token_json)
    
    @property
    def quality_check_db_path(self) -> str:
        """Get absolute path to quality check database."""
        return self.resolve_path(self.quality_check_db)


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get singleton settings instance.
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
