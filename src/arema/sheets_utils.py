"""Google Sheets utility functions for checking modifications."""

import os
import logging
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger("SheetsUtils")


def get_sheet_last_modified(
    key_file: str | None = None, sheet_id: str | None = None
) -> datetime:
    """
    Get the last modified timestamp of a Google Sheet.

    Args:
        key_file: Path to service account JSON key file (default: SERVICE_ACCOUNT_KEY env var)
        sheet_id: Google Sheet ID (default: uses module constant)

    Returns:
        datetime: Last modified timestamp in UTC

    Raises:
        Exception: If authentication fails or sheet is not accessible
    """
    key_file = key_file or os.environ.get(
        "SERVICE_ACCOUNT_KEY", "/app/service_account.json"
    )
    sheet_id = sheet_id or os.environ.get(
        "GOOGLE_SHEET_ID", "1RL6Y120_H9-yD8x52eZO44S2iLQpLoZHitcExHsPfPs"
    )

    try:
        creds = service_account.Credentials.from_service_account_file(
            key_file, scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"]
        )

        service = build("drive", "v3", credentials=creds)

        file_metadata = (
            service.files().get(fileId=sheet_id, fields="modifiedTime").execute()
        )

        mod_time_str = file_metadata.get("modifiedTime")
        mod_time = datetime.fromisoformat(mod_time_str.replace("Z", "+00:00"))

        return mod_time

    except Exception as e:
        logger.error(f"Failed to get sheet modification time: {str(e)}")
        raise


def has_sheet_been_modified_since(
    since: datetime, key_file: str | None = None, sheet_id: str | None = None
) -> bool:
    """
    Check if a Google Sheet has been modified since a given time.

    Args:
        since: Timestamp to check against
        key_file: Path to service account JSON key file
        sheet_id: Google Sheet ID

    Returns:
        bool: True if sheet was modified after 'since', False otherwise
    """
    try:
        last_modified = get_sheet_last_modified(key_file, sheet_id)

        # Ensure 'since' is timezone-aware
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)

        is_modified = last_modified > since

        if is_modified:
            logger.info(
                f"Sheet modified at {last_modified.isoformat()}, after {since.isoformat()}"
            )
        else:
            logger.info(
                f"Sheet not modified since {since.isoformat()} (last modified: {last_modified.isoformat()})"
            )

        return is_modified

    except Exception as e:
        logger.warning(
            f"Could not check sheet modification time: {str(e)}. Assuming sheet was modified."
        )
        return True
