from datetime import datetime
import requests
import json

def send_notification(message, url_thumb, url_zoom, webhook_url):
    """Send notification to Google Chat"""
    try:
            
        message = {
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
                        "altText": "Daily Report"
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

        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        response = requests.post(webhook_url, headers=headers, data=json.dumps(message))
            
        if response.status_code == 200:
            return "Successfully sent notification to Google Chat"
        else:
            raise Exception(f'Google Chat notification failed: {response.text}')
                
    except Exception as e:
            raise
    
def send_notification_prdline(message, url, webhook_url):
    """Send notification to Google Chat"""
    try:
            
        message = {
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

        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        response = requests.post(webhook_url, headers=headers, data=json.dumps(message))
            
        if response.status_code == 200:
            return "Successfully sent notification to Google Chat"
        else:
            raise Exception(f'Google Chat notification failed: {response.text}')
                
    except Exception as e:
            raise