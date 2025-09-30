"""Notification service for sending messages."""
from datetime import datetime
from time import sleep

from ..config import Settings
from ..message import send_notification, send_notification_prdline
from ..utils import get_logger


logger = get_logger(__name__)


class NotificationService:
    """Service for sending notifications to Google Chat."""
    
    def __init__(self, settings: Settings):
        """
        Initialize notification service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
    
    def send_country_report(self, thumbnail_url: str, zoom_url: str):
        """
        Send country report notification.
        
        Args:
            thumbnail_url: URL of thumbnail image
            zoom_url: URL of full-size image
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        message = f"📊 Báo cáo tiến độ kinh doanh theo Country ngày {current_date}:"
        
        logger.info("Sending country report notifications...")
        
        try:
            send_notification(message, thumbnail_url, zoom_url, self.settings.webhook_url_sso)
            logger.info("Country report sent to SSO webhook")
            
            send_notification(message, thumbnail_url, zoom_url, self.settings.webhook_url_cpi)
            logger.info("Country report sent to CPI webhook")
            
            sleep(5)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to send country report: {e}")
            raise
    
    def send_manager_report(self, thumbnail_url: str, zoom_url: str):
        """
        Send manager report notification.
        
        Args:
            thumbnail_url: URL of thumbnail image
            zoom_url: URL of full-size image
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        message = f"📊 Báo cáo tiến độ kinh doanh theo Manager ngày {current_date}:"
        
        logger.info("Sending manager report notifications...")
        
        try:
            send_notification(message, thumbnail_url, zoom_url, self.settings.webhook_url_sso)
            logger.info("Manager report sent to SSO webhook")
            
            send_notification(message, thumbnail_url, zoom_url, self.settings.webhook_url_cpi)
            logger.info("Manager report sent to CPI webhook")
            
            sleep(5)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to send manager report: {e}")
            raise
    
    def send_product_line_notification(self):
        """Send product line data notification."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        message = f"📊 Dữ liệu chi tiết theo Product Line ngày {current_date}\nLưu ý: Số liệu sẽ được overwrite theo ngày."
        
        logger.info("Sending product line notifications...")
        
        try:
            send_notification_prdline(message, self.settings.sheet_url, self.settings.webhook_url_sso)
            logger.info("Product line notification sent to SSO webhook")
            
            send_notification_prdline(message, self.settings.sheet_url, self.settings.webhook_url_cpi)
            logger.info("Product line notification sent to CPI webhook")
            
            sleep(5)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to send product line notification: {e}")
            raise
