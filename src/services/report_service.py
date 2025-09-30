"""Report generation service."""
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple
import pandas as pd

from ..config import Settings
from ..processor import formatter
from ..img import img_gen_country, img_gen_pic, upload_image, upload_image_gdrive
from ..extractor import push_dataframe_to_gsheet
from ..utils import get_logger


logger = get_logger(__name__)


class ReportService:
    """Service for generating and uploading reports."""
    
    def __init__(self, settings: Settings):
        """
        Initialize report service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        
        # Ensure output directory exists
        Path(settings.output_path).mkdir(parents=True, exist_ok=True)
    
    def generate_country_report(self, data: pd.DataFrame) -> Tuple[str, str, str]:
        """
        Generate country report with images.
        
        Args:
            data: Country data DataFrame
            
        Returns:
            Tuple of (image_path, thumbnail_url, zoom_url)
        """
        logger.info("Generating country report...")
        
        # Format data
        formatted_data = formatter(data)
        
        # Generate image
        image_path = os.path.join(
            self.settings.output_path, 
            f"country_data_{self.timestamp}.png"
        )
        img_gen_country(formatted_data, image_path)
        logger.info(f"Country image generated: {image_path}")
        
        # Upload to ImgBB
        thumbnail_url = upload_image(image_path, self.settings.imgbb_api_key)
        logger.info(f"Country image uploaded to ImgBB: {thumbnail_url}")
        
        # Upload to Google Drive
        zoom_url = upload_image_gdrive(
            image_path,
            self.settings.personal_credentials_path,
            self.settings.token_path,
            folder_id=self.settings.gdrive_folder_id
        )
        logger.info(f"Country image uploaded to Google Drive: {zoom_url}")
        
        return image_path, thumbnail_url, zoom_url
    
    def generate_manager_report(self, data: pd.DataFrame) -> Tuple[str, str, str]:
        """
        Generate manager report with images.
        
        Args:
            data: Manager data DataFrame
            
        Returns:
            Tuple of (image_path, thumbnail_url, zoom_url)
        """
        logger.info("Generating manager report...")
        
        # Format data
        formatted_data = formatter(data)
        
        # Generate image
        image_path = os.path.join(
            self.settings.output_path, 
            f"manager_data_{self.timestamp}.png"
        )
        img_gen_pic(formatted_data, image_path)
        logger.info(f"Manager image generated: {image_path}")
        
        # Upload to ImgBB
        thumbnail_url = upload_image(image_path, self.settings.imgbb_api_key)
        logger.info(f"Manager image uploaded to ImgBB: {thumbnail_url}")
        
        # Upload to Google Drive
        zoom_url = upload_image_gdrive(
            image_path,
            self.settings.personal_credentials_path,
            self.settings.token_path,
            folder_id=self.settings.gdrive_folder_id
        )
        logger.info(f"Manager image uploaded to Google Drive: {zoom_url}")
        
        return image_path, thumbnail_url, zoom_url
    
    def upload_product_line_to_gsheet(self, data: pd.DataFrame):
        """
        Upload product line data to Google Sheets.
        
        Args:
            data: Product line data DataFrame
        """
        logger.info("Uploading product line data to Google Sheets...")
        
        push_dataframe_to_gsheet(
            data,
            self.settings.google_sheet_id,
            'raw',
            self.settings.credentials_path
        )
        
        logger.info("Product line data uploaded successfully")
    
    def cleanup_old_images(self):
        """Remove old PNG files from output directory."""
        logger.info("Cleaning up old images...")
        
        output_path = Path(self.settings.output_path)
        removed_count = 0
        
        for item in output_path.glob("*.png"):
            if item.is_file():
                item.unlink()
                removed_count += 1
        
        logger.info(f"Removed {removed_count} old image(s)")
