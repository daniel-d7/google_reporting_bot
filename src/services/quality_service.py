"""Data quality check service."""
from typing import Tuple

from ..config import Settings
from ..quality_check import check_data_quality, send_error_message, send_success_message
from ..utils import get_logger


logger = get_logger(__name__)


class QualityService:
    """Service for data quality checks."""
    
    def __init__(self, settings: Settings):
        """
        Initialize quality service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
    
    def run_quality_check(self) -> Tuple[bool, float, float]:
        """
        Run data quality check.
        
        Returns:
            Tuple of (passed, current_nmv, latest_nmv)
            
        Raises:
            Exception: If quality check fails
        """
        logger.info("Starting data quality check...")
        
        try:
            quality_passed, current_nmv, latest_nmv = check_data_quality()
            
            if not quality_passed:
                logger.error(
                    f"Data quality check failed: "
                    f"Current NMV ({current_nmv:,.0f}) <= Previous NMV ({latest_nmv:,.0f})"
                )
                self.send_error_notification(current_nmv, latest_nmv)
                return False, current_nmv, latest_nmv
            else:
                logger.info(f"Data quality check passed: Current NMV ({current_nmv:,.0f})")
                return True, current_nmv, latest_nmv
                
        except Exception as e:
            logger.error(f"Data quality check error: {e}")
            try:
                self.send_error_notification(0, 0)
            except Exception as notification_error:
                logger.error(f"Failed to send error notification: {notification_error}")
            raise
    
    def send_error_notification(self, current_nmv: float, latest_nmv: float):
        """
        Send error notification.
        
        Args:
            current_nmv: Current NMV value
            latest_nmv: Latest NMV value
        """
        logger.info("Sending error notification...")
        try:
            send_error_message(current_nmv, latest_nmv)
            logger.info("Error notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
            raise
    
    def send_success_notification(self):
        """Send success notification."""
        logger.info("Sending success notification...")
        try:
            send_success_message()
            logger.info("Success notification sent successfully")
        except Exception as e:
            logger.warning(f"Failed to send success notification: {e}")
            # Don't raise - success notification failure shouldn't stop the process
