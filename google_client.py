# google_client.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import httplib2
import google_auth_httplib2

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",      # ✅ permite leer y escribir
    "https://www.googleapis.com/auth/drive.readonly",    # ✅ si vas a leer PDFs desde Drive
]

SERVICE_ACCOUNT_FILE = "service_account.json"

def sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    http = httplib2.Http(disable_ssl_certificate_validation=True)  # ⚠️ solo pruebas
    authed_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)

    return build("sheets", "v4", http=authed_http, cache_discovery=False)

def drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    http = httplib2.Http(disable_ssl_certificate_validation=True)  # ⚠️ solo pruebas
    authed_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)

    return build("drive", "v3", http=authed_http, cache_discovery=False)
