"""Image upload module for Chevereto image hosting service."""
import base64
import requests

from ..utils import get_logger


logger = get_logger(__name__)


def upload_image(image_path: str, api_key: str) -> str:
    """
    Upload image to Chevereto image hosting service.
    
    Args:
        image_path: Path to the image file
        api_key: Chevereto API key (should start with 'chv_')
    
    Returns:
        URL of the uploaded image
        
    Raises:
        Exception: If upload fails
    """
    try:
        # Chevereto API endpoint
        url = "https://img.cuongdq.cyou/api/1/upload"
        
        with open(image_path, "rb") as file:
            # Read and encode the image in base64 for Chevereto
            image_data = base64.b64encode(file.read()).decode('utf-8')
        
        # Chevereto API expects data in this format
        data = {
            "key": api_key,
            "source": image_data,
            "format": "json"
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Check if upload was successful (Chevereto format)
        if result.get("status_code") == 200 and result.get("success", {}).get("code") == 200:
            # Get the image URL from Chevereto response
            image_url = result["image"]["url"]
            
            # Convert HTTP to HTTPS for better compatibility with chat platforms
            if image_url.startswith("http://"):
                image_url = image_url.replace("http://", "https://")
            
            logger.info(f"Image uploaded successfully to {image_url}")
            return image_url
        else:
            error_message = result.get("error", {}).get("message", "Unknown error")
            raise Exception(f"Chevereto upload failed: {error_message}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during image upload: {e}")
        raise Exception(f"Network error during image upload: {str(e)}")
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise Exception(f"Image upload error: {str(e)}")
