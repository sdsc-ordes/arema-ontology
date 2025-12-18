"""Scheduled checker for Google Sheets modifications."""
import logging
from datetime import datetime, timezone
import sys
import os

# Add modules to Python path
sys.path.insert(0, os.path.join(os.getcwd(), "src/arema"))
import sheets_utils
from update_service import run_conversion

logger = logging.getLogger("ScheduledChecker")


def check_and_update(state):
    """
    Check if Google Sheet was modified and update if needed.
    
    Args:
        state: OntologyManagerState instance
        
    Returns:
        bool: True if update was performed, False otherwise
    """
    if state.is_updating:
        logger.info("Skipping scheduled check - update already in progress")
        return False
    
    try:
        check_time = datetime.now(timezone.utc)
        logger.info(f"Running scheduled check at {check_time.isoformat()}")
        
        # Check if sheet was modified since last check
        if not sheets_utils.has_sheet_been_modified_since(state.last_sheet_check_time):
            logger.info("Sheet not modified since last check - skipping update")
            state.last_sheet_check_time = check_time
            return False
        
        logger.info("Sheet has been modified - starting update")
        
        # Mark as updating to prevent concurrent checks
        state.is_updating = True
        
        # Run conversion
        run_conversion()
        
        # Update timestamps
        state.last_sheet_check_time = check_time
        state.last_update_time = check_time
        
        logger.info("Update completed successfully")
        return True
            
    except Exception as e:
        logger.error(f"Scheduled check failed: {str(e)}", exc_info=True)
        return False
    finally:
        state.is_updating = False
