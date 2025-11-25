import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OAuth 2.0 scopes for Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# File paths for credentials and token
BASE_DIR = Path(__file__).parent
CLIENT_SECRETS_FILE = str(BASE_DIR / 'credentials.json')
TOKEN_PATH = str(BASE_DIR / 'token.json')

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}. Re-authenticating.")
                if os.path.exists(TOKEN_PATH):
                    os.remove(TOKEN_PATH)
                creds = None
        if not creds:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(f"Credentials file not found at {CLIENT_SECRETS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service
