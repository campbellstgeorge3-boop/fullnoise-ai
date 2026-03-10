"""
Load Boss Assistant input from Google Drive (file or Sheet).
Uses a service account: put the JSON key path in GOOGLE_APPLICATION_CREDENTIALS,
then share the Drive file or Sheet with the service account email.
"""
import io
import tempfile
from pathlib import Path
from typing import Optional

from input_model import BossInput, ValidationError
from data_loader import load_from_path_smart

# Optional: only import when used
try:
    import google.auth
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    _HAS_GOOGLE = True
except ImportError:
    _HAS_GOOGLE = False

GOOGLE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"


def _get_drive_service(credentials_path: Optional[str] = None):
    if not _HAS_GOOGLE:
        raise ImportError(
            "Google Drive support requires: pip install google-auth google-api-python-client"
        )
    if credentials_path:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
    else:
        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
    return build("drive", "v3", credentials=creds)


def _download_file(service, file_id: str) -> tuple[bytes, str]:
    """Download file content and return (bytes, mime_type)."""
    meta = service.files().get(fileId=file_id, fields="mimeType,name").execute()
    mime = meta.get("mimeType") or ""
    if mime == GOOGLE_SHEET_MIME:
        # Export Google Sheet as CSV
        data = service.files().export(
            fileId=file_id,
            mimeType="text/csv",
        ).execute()
        return data, "text/csv"
    # Blob file: download directly
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue(), mime


def load_from_googledrive(
    file_id: str,
    company_name: Optional[str] = None,
    credentials_path: Optional[str] = None,
) -> BossInput:
    """
    Download a CSV or JSON file (or a Google Sheet exported as CSV) from Drive
    and parse into BossInput. Uses service account from credentials_path or
    GOOGLE_APPLICATION_CREDENTIALS.
    """
    service = _get_drive_service(credentials_path)
    content, mime = _download_file(service, file_id)
    # Decide extension for parsing
    if mime == GOOGLE_SHEET_MIME or "csv" in mime or "spreadsheet" in mime:
        ext = ".csv"
    elif "json" in mime:
        ext = ".json"
    else:
        # Try CSV first (common for Sheets export), then JSON
        try:
            content.decode("utf-8").strip().index("{")
            ext = ".json"
        except (ValueError, AttributeError):
            ext = ".csv"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(content)
        tmp_path = Path(f.name)
    try:
        return load_from_path_smart(tmp_path, company_name=company_name)
    finally:
        tmp_path.unlink(missing_ok=True)


def load_from_googledrive_config(config: dict) -> BossInput:
    """
    Load from Google Drive using config.
    Config: googledrive_file_id, company_name, googledrive_credentials (path to JSON)
    or set env GOOGLE_APPLICATION_CREDENTIALS and GOOGLEDRIVE_FILE_ID.
    """
    import os
    file_id = config.get("googledrive_file_id") or os.environ.get("GOOGLEDRIVE_FILE_ID")
    if file_id and hasattr(file_id, "strip"):
        file_id = file_id.strip()
    if not file_id:
        raise ValueError(
            "Set googledrive_file_id in config or GOOGLEDRIVE_FILE_ID in env"
        )
    creds_path = config.get("googledrive_credentials")
    if creds_path and hasattr(creds_path, "strip"):
        creds_path = creds_path.strip() or None
    return load_from_googledrive(
        file_id=file_id,
        company_name=config.get("company_name"),
        credentials_path=creds_path,
    )
