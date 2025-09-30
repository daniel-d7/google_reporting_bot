"""Google Drive image upload module."""
import os
import pickle
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from ..utils import get_logger


logger = get_logger(__name__)

# Scopes required for Google Drive upload
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def upload_image_gdrive(
    image_path: str,
    client_secrets_path: str,
    token_path: str,
    folder_id: Optional[str] = None
) -> str:
    """
    Upload image to Google Drive and return shareable link.
    
    Args:
        image_path: Path to the image file
        client_secrets_path: Path to Google OAuth client secrets JSON
        token_path: Path to store/load OAuth token
        folder_id: Optional Google Drive folder ID
        
    Returns:
        Shareable link to the uploaded image
        
    Raises:
        Exception: If upload fails
    """
    try:
        # Load or create credentials
        creds = _get_credentials(client_secrets_path, token_path)
        
        # Build the Drive service
        service = build('drive', 'v3', credentials=creds)
        
        # Prepare file metadata
        file_metadata = {'name': os.path.basename(image_path)}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        # Upload the file
        media = MediaFileUpload(image_path, mimetype='image/png')
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        
        # Set permissions: Anyone with the link can view
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(fileId=file_id, body=permission).execute()
        
        # Get the shareable link
        file = service.files().get(fileId=file_id, fields='webViewLink').execute()
        shareable_link = file.get('webViewLink')
        
        logger.info(f"Image uploaded to Google Drive: {shareable_link}")
        return shareable_link
        
    except Exception as e:
        logger.error(f"Google Drive upload failed: {e}")
        raise Exception(f"Google Drive upload failed: {str(e)}")


def _get_credentials(client_secrets_path: str, token_path: str) -> Credentials:
    """
    Load or create Google OAuth credentials.
    
    Args:
        client_secrets_path: Path to client secrets JSON
        token_path: Path to token file
        
    Returns:
        Valid credentials
    """
    creds = None
    
    # Load existing token if available
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing Google OAuth token...")
            creds.refresh(Request())
        else:
            logger.info("Creating new Google OAuth token...")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, 
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        logger.info(f"Token saved to {token_path}")
    
    return creds
