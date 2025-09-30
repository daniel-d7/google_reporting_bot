"""
Google Reporting Bot - Main Entry Point

This script orchestrates the daily business reporting process including:
- Data quality validation
- Data extraction from database
- Report generation with charts
- Upload to Google Drive and image hosting
- Notification sending via Google Chat
"""
import sys
from time import sleep

from src.config import get_settings
from src.services import DataService, ReportService, NotificationService, QualityService
from src.utils import setup_logger, get_logger


def main():
    """Main entry point for the reporting bot."""
    # Setup logging
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("Starting Google Reporting Bot")
    logger.info("=" * 80)
    
    try:
        # Load and validate configuration
        settings = get_settings()
        is_valid, missing_vars = settings.validate()
        
        if not is_valid:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            sys.exit(1)
        
        logger.info("Configuration loaded and validated successfully")
        
        # Initialize services
        quality_service = QualityService(settings)
        data_service = DataService(settings)
        report_service = ReportService(settings)
        notification_service = NotificationService(settings)
        
        # Step 1: Data Quality Check
        logger.info("-" * 80)
        logger.info("STEP 1: Data Quality Check")
        logger.info("-" * 80)
        
        quality_passed, current_nmv, latest_nmv = quality_service.run_quality_check()
        
        if not quality_passed:
            logger.error("Data quality check failed. Exiting...")
            sys.exit(1)
        
        # Step 2: Extract Data
        logger.info("-" * 80)
        logger.info("STEP 2: Extract Data from Database")
        logger.info("-" * 80)
        
        country_data = data_service.extract_country_data()
        manager_data = data_service.extract_manager_data()
        prdline_data = data_service.extract_product_line_data()
        
        if country_data is None or manager_data is None or prdline_data is None:
            logger.error("Failed to extract data from database")
            quality_service.send_error_notification(0, 0)
            sys.exit(1)
        
        # Step 3: Generate Reports
        logger.info("-" * 80)
        logger.info("STEP 3: Generate Reports")
        logger.info("-" * 80)
        
        # Generate country report
        _, country_thumbnail, country_zoom = report_service.generate_country_report(country_data)
        sleep(10)  # Rate limiting
        
        # Generate manager report
        _, manager_thumbnail, manager_zoom = report_service.generate_manager_report(manager_data)
        sleep(10)  # Rate limiting
        
        # Upload product line data to Google Sheets
        report_service.upload_product_line_to_gsheet(prdline_data)
        
        # Step 4: Send Notifications
        logger.info("-" * 80)
        logger.info("STEP 4: Send Notifications")
        logger.info("-" * 80)
        
        notification_service.send_country_report(country_thumbnail, country_zoom)
        notification_service.send_manager_report(manager_thumbnail, manager_zoom)
        notification_service.send_product_line_notification()
        
        # Step 5: Cleanup
        logger.info("-" * 80)
        logger.info("STEP 5: Cleanup")
        logger.info("-" * 80)
        
        report_service.cleanup_old_images()
        
        # Step 6: Send Success Notification
        logger.info("-" * 80)
        logger.info("STEP 6: Send Success Notification")
        logger.info("-" * 80)
        
        quality_service.send_success_notification()
        
        logger.info("=" * 80)
        logger.info("Google Reporting Bot completed successfully!")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()