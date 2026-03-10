"""
Google Drive OAuth (Installed App flow). User signs in with their Google account.
Credentials: google_oauth_client.json. Token: token.json (auto-refresh).
No service accounts.
"""
import json
import os
from pathlib import Path
from typing import Optional

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
ROOT = Path(__file__).resolve().parent
CREDENTIALS_FILE = ROOT / "google_oauth_client.json"
TOKEN_FILE = ROOT / "token.json"
DEFAULT_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "1hBut7Sp1JOMwOsoIik2-035gwSU92kU5")


def _get_credentials_path() -> Path:
    return CREDENTIALS_FILE


def _get_token_path() -> Path:
    return TOKEN_FILE


def run_oauth_flow() -> None:
    """
    Launch browser for user sign-in and save token to token.json.
    Requires google_oauth_client.json in project root (download from Google Cloud Console).
    """
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError as e:
        raise ImportError(
            "Google Drive OAuth requires: pip install google-auth google-auth-oauthlib google-api-python-client"
        ) from e

    creds = None
    token_path = _get_token_path()
    creds_path = _get_credentials_path()
    if not creds_path.is_file():
        raise FileNotFoundError(
            f"Credentials file not found: {creds_path}\n"
            "Download OAuth client JSON from Google Cloud Console (Desktop app) and save as google_oauth_client.json"
        )

    if token_path.is_file():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    print(f"Token saved to {token_path}")


def get_drive_service():
    """Build Drive API service using token.json (refreshes if expired)."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as e:
        raise ImportError(
            "Google Drive requires: pip install google-auth google-api-python-client"
        ) from e

    token_path = _get_token_path()
    if not token_path.is_file():
        raise FileNotFoundError(
            f"Token not found: {token_path}. Run: python main.py --drive-auth"
        )
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def list_pdfs_in_folder(folder_id: str) -> list[dict]:
    """List all PDF files in the given Drive folder. Returns list of {id, name}."""
    service = get_drive_service()
    q = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
    results = service.files().list(q=q, fields="files(id,name)", pageSize=100).execute()
    return results.get("files", [])


def download_pdf(service, file_id: str) -> bytes:
    """Download a single file by ID; returns raw bytes."""
    from googleapiclient.http import MediaIoBaseDownload
    import io
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def sync_pdfs_from_drive(
    folder_id: str,
    out_dir: Path,
) -> list[Path]:
    """
    List PDFs in the Drive folder, download each to out_dir, return list of saved paths.
    """
    service = get_drive_service()
    files = list_pdfs_in_folder(folder_id)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for f in files:
        fid, name = f.get("id"), f.get("name", "unknown.pdf")
        if not fid:
            continue
        if not name.lower().endswith(".pdf"):
            name = name + ".pdf"
        content = download_pdf(service, fid)
        path = out_dir / name
        path.write_bytes(content)
        saved.append(path)
    return saved
