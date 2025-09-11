import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_image_gdrive(image_path, client_secrets_path, token_path, folder_id=None):
    try:
        # Define scopes
        scopes = ['https://www.googleapis.com/auth/drive.file']

        # Load or create credentials
        creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        # Build the Drive service
        service = build('drive', 'v3', credentials=creds)

        # File metadata
        file_metadata = {'name': os.path.basename(image_path)}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Upload the file (adjust mimetype based on image type if needed, e.g., 'image/jpeg')
        media = MediaFileUpload(image_path, mimetype='image/png')  # Change to 'image/jpeg' for JPG, etc.

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
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

        return shareable_link

    except Exception as e:
        raise Exception(f"Google Drive upload failed: {str(e)}")