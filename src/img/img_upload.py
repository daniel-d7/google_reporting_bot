import base64
import requests


def upload_image(image_path, api_key):
    try:
        url = "https://api.imgbb.com/1/upload"
            
        with open(image_path, "rb") as file:
            files = {"image": file}
            data = {"key": api_key}
                
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
                
            result = response.json()
            if result.get("success"):
                image_url = result["data"]["url"]
                return image_url
            else:
                raise Exception(f"ImgBB upload failed: {result.get('error', 'Unknown error')}")
                    
    except Exception as e:
        raise