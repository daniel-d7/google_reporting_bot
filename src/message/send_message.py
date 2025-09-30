"""Google Chat messaging module."""
from datetime import datetime
import requests
import json
from typing import Dict, Any

from ..utils import get_logger


logger = get_logger(__name__)


def send_notification(
    message: str,
    url_thumb: str,
    url_zoom: str,
    webhook_url: str
) -> str:
    """
    Send notification with image to Google Chat.
    
    Args:
        message: Message text to send
        url_thumb: URL of thumbnail image
        url_zoom: URL of full-size image
        webhook_url: Google Chat webhook URL
        
    Returns:
        Success message
        
    Raises:
        Exception: If notification fails
    """
    try:
        # Ensure URLs use HTTPS for better compatibility
        url_thumb = _ensure_https(url_thumb)
        url_zoom = _ensure_https(url_zoom)
        
        message_payload = _build_image_card(message, url_thumb, url_zoom)
        
        logger.debug(f"Sending image URL: {url_thumb}")
        logger.debug(f"Zoom URL: {url_zoom}")
        
        response = _send_webhook(webhook_url, message_payload)
        
        logger.info(f"Notification sent successfully to {webhook_url}")
        return "Successfully sent notification to Google Chat"
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise


def send_notification_prdline(
    message: str,
    url: str,
    webhook_url: str
) -> str:
    """
    Send product line notification to Google Chat.
    
    Args:
        message: Message text to send
        url: URL to the detailed report
        webhook_url: Google Chat webhook URL
        
    Returns:
        Success message
        
    Raises:
        Exception: If notification fails
    """
    try:
        message_payload = _build_link_card(message, url)
        
        response = _send_webhook(webhook_url, message_payload)
        
        logger.info(f"Product line notification sent successfully to {webhook_url}")
        return "Successfully sent notification to Google Chat"
        
    except Exception as e:
        logger.error(f"Failed to send product line notification: {e}")
        raise


def _ensure_https(url: str) -> str:
    """Convert HTTP URLs to HTTPS."""
    if url.startswith("http://"):
        return url.replace("http://", "https://")
    return url


def _build_image_card(
    message: str,
    url_thumb: str,
    url_zoom: str
) -> Dict[str, Any]:
    """
    Build Google Chat card with image and link.
    
    Args:
        message: Message text
        url_thumb: Thumbnail URL
        url_zoom: Full image URL
        
    Returns:
        Google Chat card payload
    """
    return {
        "cardsV2": [
            {
                "card": {
                    "header": {
                        "title": "Daily Report"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {"text": message}
                                },
                                {
                                    "image": {
                                        "imageUrl": url_thumb,
                                        "altText": "Daily Report Chart",
                                        "onClick": {
                                            "openLink": {
                                                "url": url_zoom
                                            }
                                        }
                                    }
                                },
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Open Full Image to Zoom",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": url_zoom
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }


def _build_link_card(message: str, url: str) -> Dict[str, Any]:
    """
    Build Google Chat card with link button.
    
    Args:
        message: Message text
        url: Link URL
        
    Returns:
        Google Chat card payload
    """
    return {
        "cardsV2": [
            {
                "card": {
                    "header": {
                        "title": "Detail by Productline Report"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {"text": message}
                                },
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Click on the link to see the detail report by productlines",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": url
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }


def _send_webhook(webhook_url: str, payload: Dict[str, Any]) -> requests.Response:
    """
    Send payload to Google Chat webhook.
    
    Args:
        webhook_url: Webhook URL
        payload: Message payload
        
    Returns:
        Response object
        
    Raises:
        Exception: If webhook call fails
    """
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code != 200:
        raise Exception(f'Google Chat notification failed: {response.text}')
    
    return response
