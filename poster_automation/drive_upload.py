import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .logger import log
from .config import CONFIG

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_auth_client(oauth_credentials=None, token_file=None):
    oauth_credentials = oauth_credentials or CONFIG["oauth_credentials"]
    token_file        = token_file        or CONFIG["token_file"]

    creds = None

    # Load existing token
    if os.path.exists(token_file):
     try:
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
     except Exception:
        os.remove(token_file)
        creds = None

    # Refresh or re-authorize if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(oauth_credentials, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(token_file, "w") as f:
            f.write(creds.to_json())
        log("Token saved!")

    return creds

def upload_to_drive(file_path, drive_folder_id=None, oauth_credentials=None, token_file=None):
    drive_folder_id = drive_folder_id or CONFIG["drive_folder_id"]

    log("Authenticating with Google Drive...")
    creds = get_auth_client(oauth_credentials, token_file)
    drive = build("drive", "v3", credentials=creds)

    file_name = os.path.basename(file_path)
    log(f"Uploading {file_name} to Drive...")

    file_metadata = {
        "name":    file_name,
        "parents": [drive_folder_id],
    }
    media = MediaFileUpload(file_path, mimetype="image/png", resumable=True)

    res = drive.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    log(f"Uploaded! File ID: {res['id']}")
    log(f"View: {res['webViewLink']}")
    return res["webViewLink"]
