import base64
import requests


def upload_image(image_path, api_key):
    """
    Upload image to Chevereto image hosting service
    
    Args:
        image_path (str): Path to the image file
        api_key (str): Chevereto API key (should start with 'chv_')
    
    Returns:
        str: URL of the uploaded image
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
            
            return image_url
        else:
            error_message = result.get("error", {}).get("message", "Unknown error")
            raise Exception(f"Chevereto upload failed: {error_message}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during image upload: {str(e)}")
    except Exception as e:
        raise Exception(f"Image upload error: {str(e)}")